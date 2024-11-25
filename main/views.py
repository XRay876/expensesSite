from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import *
import json
from decimal import Decimal
import re

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User

from django.utils import timezone
from django.db.models import Sum
from django.db.models.functions import TruncDay, TruncMonth
from django.contrib import messages

# import openai
import groq
import os
from auth_data import groq_key


@login_required
def home(request):
    if request.user.is_authenticated:
        sort_order = request.GET.get('sort', 'created_at_new')

        blocks = MoneyBlock.objects.filter(user=request.user).prefetch_related('transactions')

        if sort_order == 'decrease':
            blocks = blocks.order_by('-balance')
        elif sort_order == 'increase':
            blocks = blocks.order_by('balance')
        elif sort_order == 'created_at_new':
            blocks = blocks.order_by(f'-created_at')
        elif sort_order == 'created_at_old':
            blocks = blocks.order_by(f'created_at')
        else:
            blocks = blocks.order_by('name')

        block_transactions = {}
        for block in blocks:
            transactions = block.transactions.order_by('-date').values('id', 'description', 'amount', 'date')
            block_transactions[block.id] = [
                {
                    'id': transaction['id'],
                    'description': transaction['description'],
                    'amount': float(transaction['amount']),
                    'date': transaction['date'].isoformat(),
                    # 'date': transaction['date'].strftime('%m-%d-%Y %H:%M'),
                }
                for transaction in block.transactions.values('id', 'description', 'amount', 'date')
            ]

        if request.method == 'POST':
            form = MoneyBlockForm(request.POST)
            if form.is_valid():
                block = form.save(commit=False)
                block.user = request.user
                block.save()
                messages.success(request, 'Block created successfully.')
                return redirect('home')
            else:
                messages.error(request, 'An error occurred while creating the block.')
        else:
            form = MoneyBlockForm()

        top_up_form = TopUpForm()
        transactionForm = TransactionForm()

        user_profile, created = Profile.objects.get_or_create(user=request.user)

        return render(request, 'home.html', {
            'form': form,
            'blocks': blocks,
            'block_transactions': json.dumps(block_transactions),
            'formTransaction': transactionForm,
            'top_up_form': top_up_form,
            'sort': sort_order,
            'unique_link': str(user_profile.unique_link),
        })
    return render(request, 'home.html')


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = CustomAuthenticationForm()

    return render(request, 'login.html', {'form': form})


@login_required
@require_POST
def add_transaction(request):
    form = TransactionForm(request.POST)
    if form.is_valid():
        transaction = form.save(commit=False)
        money_block = transaction.money_block

        transaction.amount = -abs(transaction.amount)
        transaction.save()

        money_block.balance += transaction.amount
        money_block.save()

        return JsonResponse({
            'success': True,
            'transaction': {
                'id': transaction.id,
                'description': transaction.description,
                'amount': float(transaction.amount),

                'date': transaction.date.isoformat(),
                'money_block': transaction.money_block.id,
            },
            'new_balance': float(money_block.balance),
            'currency': money_block.currency,
        })
    else:
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@login_required
@require_http_methods(["DELETE"])
def delete_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, money_block__user=request.user)

    money_block = transaction.money_block
    if transaction.amount <= 0:
        money_block.balance += abs(transaction.amount)
    elif transaction.amount > 0:
        money_block.balance -= abs(transaction.amount)

    money_block.save()

    transaction.delete()
    return JsonResponse({
        'success': True,
        'new_balance': float(money_block.balance),
        'currency': money_block.currency,
    })


@login_required
@require_http_methods(["DELETE"])
def delete_block(request, money_block_id):
    money_block = get_object_or_404(MoneyBlock, id=money_block_id, user=request.user)
    money_block.transactions.all().delete()
    money_block.delete()
    return JsonResponse({'success': True, 'message': 'Block deleted successfully.'})


@login_required
@require_POST
def top_up_balance(request):
    form = TopUpForm(request.POST)
    if form.is_valid():
        money_block_id = form.cleaned_data['money_block']
        top_up_amount = form.cleaned_data['amount']

        money_block = get_object_or_404(MoneyBlock, id=money_block_id, user=request.user)

        money_block.balance += abs(top_up_amount)
        money_block.save()

        transaction = Transaction.objects.create(
            money_block=money_block,
            description="Top Up",
            amount=top_up_amount
        )

        return JsonResponse({
            'success': True,
            'message': 'Balance topped up successfully.',
            'new_balance': float(money_block.balance),
            'currency': money_block.currency,
            'transaction': {
                'id': transaction.id,
                'description': transaction.description,
                'amount': float(transaction.amount),
                'date': transaction.date.isoformat(),
                'money_block': transaction.money_block.id,
            }
        })
    else:
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@login_required()
def shared_page(request, unique_link):
    profile = get_object_or_404(Profile, unique_link=unique_link)
    user = profile.user
    sort_order = request.GET.get('sort', 'created_at_new')
    blocks = MoneyBlock.objects.filter(user=user).prefetch_related('transactions')

    if sort_order == 'decrease':
        blocks = blocks.order_by('-balance')
    elif sort_order == 'increase':
        blocks = blocks.order_by('balance')
    elif sort_order == 'created_at_new':
        blocks = blocks.order_by(f'-created_at')
    elif sort_order == 'created_at_old':
        blocks = blocks.order_by(f'created_at')
    else:
        blocks = blocks.order_by('name')

    block_transactions = {}
    for block in blocks:
        transactions = block.transactions.order_by('-date').values('id', 'description', 'amount', 'date')
        block_transactions[block.id] = [
            {
                'id': transaction['id'],
                'description': transaction['description'],
                'amount': float(transaction['amount']),
                'date': transaction['date'].isoformat(),
            }
            for transaction in block.transactions.values('id', 'description', 'amount', 'date')
        ]

    return render(request, 'shared_page.html', {
        'blocks': blocks,
        'block_transactions': json.dumps(block_transactions),
        'shared_user': user,
        'sort': sort_order,
        'unique_link': str(profile.unique_link),
    })


# @login_required
# def get_graph_data(request, money_block_id):
#     money_block = get_object_or_404(MoneyBlock, id=money_block_id, user=request.user)
#     transactions = money_block.transactions.all()
#
#     now = timezone.now()
#     current_year = now.year
#     current_month = now.month
#
#     monthly_transactions = transactions.filter(
#         date__year=current_year,
#         date__month=current_month,
#         amount__lt=0
#     )
#
#     daily_expenses = monthly_transactions.annotate(
#         day=TruncDay('date')
#     ).values('day').annotate(
#         total=Sum('amount')
#     ).order_by('day')
#
#     daily_expenses_data = [
#         {
#             'day': expense['day'].strftime('%Y-%m-%d'),
#             'total': float(-expense['total'])
#         }
#         for expense in daily_expenses
#     ]
#
#     monthly_expenses = transactions.filter(amount__lt=0).annotate(
#         month=TruncMonth('date')
#     ).values('month').annotate(
#         total=Sum('amount')
#     ).order_by('month')
#
#     monthly_expenses_data = [
#         {
#             'month': expense['month'].strftime('%Y-%m'),
#             'total': float(-expense['total'])
#         }
#         for expense in monthly_expenses
#     ]
#
#     return JsonResponse({
#         'daily_expenses': daily_expenses_data,
#         'monthly_expenses': monthly_expenses_data,
#     })

@login_required
def get_graph_data(request, money_block_id):
    money_block = get_object_or_404(MoneyBlock, id=money_block_id, user=request.user)
    transactions = money_block.transactions.all()

    now = timezone.now()
    current_year = now.year
    current_month = now.month

    monthly_expense_transactions = transactions.filter(amount__lt=0)

    daily_expenses = transactions.filter(
        date__year=current_year,
        date__month=current_month,
        amount__lt=0
    ).annotate(
        day=TruncDay('date')
    ).values('day').annotate(
        total=Sum('amount')
    ).order_by('day')

    daily_expenses_data = [
        {
            'day': expense['day'].strftime('%Y-%m-%d'),
            'total': float(-expense['total'])
        }
        for expense in daily_expenses
    ]

    monthly_expenses = monthly_expense_transactions.annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')

    monthly_expenses_data = [
        {
            'month': expense['month'].strftime('%Y-%m'),
            'total': float(-expense['total'])
        }
        for expense in monthly_expenses
    ]

    monthly_topup_transactions = transactions.filter(amount__gt=0)

    daily_topups = transactions.filter(
        date__year=current_year,
        date__month=current_month,
        amount__gt=0
    ).annotate(
        day=TruncDay('date')
    ).values('day').annotate(
        total=Sum('amount')
    ).order_by('day')

    daily_topups_data = [
        {
            'day': topup['day'].strftime('%Y-%m-%d'),
            'total': float(topup['total'])
        }
        for topup in daily_topups
    ]

    monthly_topups = monthly_topup_transactions.annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')

    monthly_topups_data = [
        {
            'month': topup['month'].strftime('%Y-%m'),
            'total': float(topup['total'])
        }
        for topup in monthly_topups
    ]

    return JsonResponse({
        'daily_expenses': daily_expenses_data,
        'monthly_expenses': monthly_expenses_data,
        'daily_topups': daily_topups_data,
        'monthly_topups': monthly_topups_data,
    })


def get_graph_data_shared(request, unique_link, money_block_id):
    profile = get_object_or_404(Profile, unique_link=unique_link)
    user = profile.user
    money_block = get_object_or_404(MoneyBlock, id=money_block_id, user=user)
    transactions = money_block.transactions.all()

    now = timezone.now()
    current_year = now.year
    current_month = now.month

    # Expenses
    daily_expenses = transactions.filter(
        date__year=current_year,
        date__month=current_month,
        amount__lt=0
    ).annotate(
        day=TruncDay('date')
    ).values('day').annotate(
        total=Sum('amount')
    ).order_by('day')

    daily_expenses_data = [
        {
            'day': expense['day'].strftime('%Y-%m-%d'),
            'total': float(-expense['total'])
        }
        for expense in daily_expenses
    ]

    monthly_expenses = transactions.filter(amount__lt=0).annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')

    monthly_expenses_data = [
        {
            'month': expense['month'].strftime('%Y-%m'),
            'total': float(-expense['total'])
        }
        for expense in monthly_expenses
    ]

    # Top-ups
    daily_topups = transactions.filter(
        date__year=current_year,
        date__month=current_month,
        amount__gt=0
    ).annotate(
        day=TruncDay('date')
    ).values('day').annotate(
        total=Sum('amount')
    ).order_by('day')

    daily_topups_data = [
        {
            'day': topup['day'].strftime('%Y-%m-%d'),
            'total': float(topup['total'])
        }
        for topup in daily_topups
    ]

    monthly_topups = transactions.filter(amount__gt=0).annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')

    monthly_topups_data = [
        {
            'month': topup['month'].strftime('%Y-%m'),
            'total': float(topup['total'])
        }
        for topup in monthly_topups
    ]

    return JsonResponse({
        'daily_expenses': daily_expenses_data,
        'monthly_expenses': monthly_expenses_data,
        'daily_topups': daily_topups_data,
        'monthly_topups': monthly_topups_data,
    })


@login_required
def plan(request):
    money_blocks = MoneyBlock.objects.filter(user=request.user).prefetch_related('transactions')

    max_transactions = 0
    threshold = 20
    block_data = []
    for block in money_blocks:
        transactions = block.transactions.order_by('-date')
        transaction_list = list(transactions)
        max_transactions = max(max_transactions, len(transaction_list))
        block_data.append({
            'block': block,
            'transactions': transaction_list,
        })

    return render(request, 'plan.html', {
        'blocks': block_data,
        'max_transactions': max_transactions + threshold,
    })


# openai.api_key = openai_key

client = groq.Groq(
    api_key=groq_key,
)


@login_required
def process_ai_data(request):
    if request.method == 'POST':

        try:

            body_unicode = request.body.decode('utf-8')
            body_data = json.loads(body_unicode)
            data = body_data.get('data', None)

            if data:

                table_data = json.loads(data)
                prompt = generate_prompt(table_data)

                try:

                    chat_completion = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant that processes financial data."},
                            {"role": "user", "content": prompt}
                        ],
                        model="llama3-8b-8192",
                    )

                    ai_output = chat_completion.choices[0].message.content

                    ai_output = clean_ai_output(ai_output)
                    
                    processed_data = json.loads(ai_output)


                    return JsonResponse({'processed_data': processed_data})
                except Exception as e:
                    print(e)
                    return JsonResponse({'error': 'An error occurred while processing the data.'}, status=500)
            else:
                return JsonResponse({'error': 'No data provided.'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)


def generate_prompt(table_data):

    prompt = (
        f"Given the following financial data in JSON format:\n"
        f"{json.dumps(table_data)}\n\n"
        "Please perform the following tasks:\n"
        "1. Analyze the data.\n"
        "2. Find the most valuable transaction in data and provide notes - why.\n"
        "3. Calculate the total balance.\n"
        "4. Mandatory provide any additional insights that might be helpful based on data.\n"
        "5. Mandatory provide additional notes (full sentences) based on data in JSON format in appropriate place."
        "If it more than 1 sentence that add another 'Note' : 'Text', dont put more than "
        "1 sentence in one JSON cell! Mandatory rule: No text in your output can be without JSON format!\n\n"
        "Important Instructions:\n"
        "- Return the processed data in valid JSON format.\n"
        "- Do not include any empty keys or keys with empty strings as values.\n"
        "- Ensure that each transaction object contains only valid key-value pairs.\n"
        "- Exclude any entries with empty headers or keys from the output.\n"
        "- Do not include any code or extra notes outside of the JSON data.\n"
        "- I will need this output to insert it in the table structure, so your output"
        "cant have any words outside the JSON structure. Your output have to begin from JSON structure and"
        " finish with JSON structure.\n\n"
        "Example of the expected JSON output:\n"
        "{\n"
        "  \"Big Valuable Transactions\": [\n"
        "    {\n"
        "      \"Block Name\": \"Tuition money\",\n"
        "      \"Description\": \"Top Up: Oct. 28, 2024, 11:30 p.m.\",\n"
        "      \"Amount\": +1000.00,\n"
        "      \"Valuable because\": \"The biggest expense on food\"\n"
        "    },\n"
        "    {\n"
        "      \"Block Name\": \"Tuition money\",\n"
        "      \"Description\": \"Purchase: Oct. 26, 2024, 9:30 a.m.\",\n"
        "      \"Amount\": -500.00,\n"
        "      \"Valuable because\": \"The smallest expense on clothes\"\n"
        "    }\n"
        "  ],\n"
        "  \"total_balance\": {\n"
        "    \"Total Balance\": 1500.00,\n"
        "  },\n"
        "  \"additional_insights\": {\n"
        "    \"Highest Transaction\": 1000.00,\n"
        "    \"Lowest_transaction\": 500.00,\n"
        "    \"Average Spend\": 750.00\n"
        "    \"Average Top up\": 750.00\n"
        "    \"Note_1\": \"Imagine helpful note based on data provided\"\n"
        "    \"Note_2\": \"Imagine helpful note based on data provided\"\n"
        "    \"Note_3\": \"Imagine helpful note based on data provided\"\n"
        "  },\n"
        "  \"monthly\": [\n"
        "   {\n"
        "    \"Month\": \"October\""
        "    \"Money spend on food\": 1000.00,\n"
        "    \"Money spend on hobbies\": 500.00,\n"
        "    \"Add more\": 750.00\n"
        "    \"Add more\": 750.00\n"
        "    \"additional note about spending in this month\": \"Imagine helpful note based on data provided\"\n"
        "    \"additional note about spending in this month\": \"Imagine helpful note based on data provided\"\n"
        "    \"additional note about spending in this month\": \"Imagine helpful note based on data provided\"\n"
        "  },\n"
        "  {\n "
        "    \"Month\": \"November\""
        "    \"Money spend on food\": 1000.00,\n"
        "    \"Money spend on hobbies\": 500.00,\n"
        "    \"Add more\": 750.00\n"
        "    \"Add more\": 750.00\n"
        "    \"additional note about spending in this month\": \"Imagine helpful note based on data provided\"\n"
        "    \"additional note about spending in this month\": \"Imagine helpful note based on data provided\"\n"
        "    \"additional note about spending in this month\": \"Imagine helpful note based on data provided\"\n"
        "  }\n"
        "  ]\n"
        "}\n\n"
        "The mandatory rule for your output, that NO TEXT HAS TO BE WITHOUT JSON STRUCTURE"
    )
    return prompt


def clean_ai_output(ai_output):

    ai_output = ai_output.strip()
    ai_output = ai_output.replace('```json', '')
    ai_output = ai_output.replace('```', '')
    ai_output = ai_output.strip()


    def extract_json_from_text(text):
        brace_stack = []
        json_start = -1
        json_end = -1
        for i, c in enumerate(text):
            if c == '{':
                if not brace_stack:
                    json_start = i
                brace_stack.append('{')
            elif c == '}':
                if brace_stack:
                    brace_stack.pop()
                    if not brace_stack:
                        json_end = i + 1
                        break
        if json_start != -1 and json_end != -1:
            json_str = text[json_start:json_end]
            return json_str
        else:
            return ''

    json_str = extract_json_from_text(ai_output)
    if not json_str:
        return ''

    try:
        json_data = json.loads(json_str)
        return json.dumps(json_data)
    except json.JSONDecodeError:

        json_str_fixed = json_str.replace("'", '"')
        json_str_fixed = re.sub(r',\s*([\]}])', r'\1', json_str_fixed)
        json_str_fixed = re.sub(r'//.*', '', json_str_fixed)
        json_str_fixed = re.sub(r'/\*.*?\*/', '', json_str_fixed, flags=re.DOTALL)

        try:
            json_data = json.loads(json_str_fixed)
            return json.dumps(json_data)
        except json.JSONDecodeError:

            return ''

