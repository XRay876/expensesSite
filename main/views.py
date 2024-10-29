from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import *
import json
from decimal import Decimal

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User

from django.utils import timezone
from django.db.models import Sum
from django.db.models.functions import TruncDay, TruncMonth
from django.contrib import messages

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