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
                # print(prompt)
                try:

                    chat_completion = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant that processes financial data."},
                            {"role": "user", "content": prompt}
                        ],
                        model="llama3-8b-8192",
                    )

                    ai_output = chat_completion.choices[0].message.content
                    # print(ai_output)
                    ai_output = clean_ai_output(ai_output)
                    # print('------')
                    # print(ai_output)
                    processed_data = json.loads(ai_output)
                    print(processed_data)

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
    # prompt = f"Given the following financial data in JSON format:\n{json.dumps(table_data)}\n\n"
    # prompt += "Please analyze the data, sort the transactions by amount in descending order, "
    # prompt += "calculate the total balance, and provide any additional insights that might be helpful. "
    # prompt += "Return the processed data in JSON format, matching the structure of the input data."
    # prompt += "Don't give me any code or extra notes. Give me only JSON data. Example of output: "
    # prompt += "{ 'name_of_money_block' : 'data', '...', '...'},{ 'name_of_money_block' : .... }..."
    # prompt += ("Add any notes about additional insight that might be helpful,"
    #            "like Sum or Median or Any thoughts, so put it in the same JSON format, like:")
    # prompt += "{ 'additional Note' : 'Note', 'Note'}, {'Another note':'Note','Note'}..."
    # prompt += "The mandatory rule for your output, that NO TEXT HAS TO BE WITHOUT JSON STRUCTURE"

    prompt = (
        f"Given the following financial data in JSON format:\n"
        f"{json.dumps(table_data)}\n\n"
        "Please perform the following tasks:\n"
        "1. Analyze the data.\n"
        "2. Sort the transactions by amount in descending order.\n"
        "3. Calculate the total balance.\n"
        "4. Provide any additional insights that might be helpful based on data.\n\n"
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
        "  \"sorted_transactions\": [\n"
        "    {\n"
        "      \"transaction_block_name\": \"Tuition money\",\n"
        "      \"description\": \"Top Up\",\n"
        "      \"amount\": +1000.00\n"
        "    },\n"
        "    {\n"
        "      \"transaction_block_name\": \"Tuition money\",\n"
        "      \"description\": \"Purchase\",\n"
        "      \"amount\": -500.00\n"
        "    }\n"
        "  ],\n"
        "  \"total_balance\": 1500.00,\n"
        "  \"additional_insights\": {\n"
        "    \"highest_transaction\": 1000.00,\n"
        "    \"lowest_transaction\": 500.00,\n"
        "    \"average_transaction\": 750.00\n"
        "    \"additional_note_about_spending_1\": You need to spend less money on hobbies\n"
        "    \"additional_note_about_spending_2\": Text\n"
        "    \"additional_note_about_spending_3\": Text\n"
        "  }\n"
        "}\n"
        "The mandatory rule for your output, that NO TEXT HAS TO BE WITHOUT JSON STRUCTURE"
    )
    return prompt


def clean_ai_output(ai_output):
    ai_output = re.sub(r',\s*([}\]])', r'\1', ai_output)
    indexes = []
    for i in range(len(ai_output)):
        if ai_output[i] in "{}":
            indexes.append(i)

    ai_output = ai_output[int(indexes[0]):int(indexes[-1])+1]
    return ai_output
