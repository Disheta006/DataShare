from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.core.paginator import Paginator
from core.models import User
from .models import Transfer

# Create your views here.
@login_required
def transfer(request):

    data_options = ["50MB", "100MB", "150MB", "200MB", "500MB", "1GB"]

    if request.method == "POST":

        sender = request.user
        receiver_mobile = request.POST.get("receiver_number")
        amount_input = request.POST.get("customer_amount")

        # 🔹 Validate receiver
        try:
            receiver = User.objects.get(mobile=receiver_mobile)
        except User.DoesNotExist:
            messages.error(request, "Receiver not found")
            return redirect("transfer")

        # 🔹 Prevent self transfer
        if sender == receiver:
            messages.error(request, "You cannot transfer to yourself")
            return redirect("transfer")

        # 🔹 Validate amount
        if not amount_input:
            messages.error(request, "Please enter amount")
            return redirect("transfer")

        try:
            amount = int(amount_input)
        except:
            messages.error(request, "Invalid amount")
            return redirect("transfer")

        # 🔹 Business rules
        if amount < 50:
            messages.error(request, "Minimum transfer is 50MB")
            return redirect("transfer")

        if amount > 1024:
            messages.error(request, "Maximum transfer is 1GB")
            return redirect("transfer")

        # 🔹 One transfer per day rule
        today = timezone.now().date()
        already_transferred = Transfer.objects.filter(
            sender=sender,
            created_at__date=today,
            status="success"
        ).exists()

        if already_transferred:
            messages.error(request, "You can only transfer once per day")
            return redirect("transfer")

        # 🔹 Balance check
        if sender.data_balance < amount:
            messages.error(request, "Insufficient data balance")
            return redirect("transfer")

        # 🔐 ATOMIC TRANSACTION (VERY IMPORTANT)
        try:
            with transaction.atomic():

                sender.data_balance -= amount
                receiver.data_balance += amount

                sender.save()
                receiver.save()

                Transfer.objects.create(
                    sender=sender,
                    receiver=receiver,
                    amount=amount,
                    status="success"
                )

        except Exception as e:

            Transfer.objects.create(
                sender=sender,
                receiver=receiver,
                amount=amount,
                status="failed",
                reason=str(e)
            )

            messages.error(request, "Transfer failed. Try again.")
            return redirect("transfer")

        messages.success(request, f"{amount}MB transferred successfully 🎉")
        return redirect("transfer")

    return render(request, 'transfers/transfer.html', {
        'data_options': data_options
    })

@login_required
def history(request):

    user = request.user

    transactions = Transfer.objects.filter(
        sender=user
    ) | Transfer.objects.filter(
        receiver=user
    )

    transactions = transactions.order_by('-created_at')

    paginator = Paginator(transactions, 10)
    page = request.GET.get('page')

    transactions = paginator.get_page(page)

    return render(request, "transfers/history.html", {
        "transactions": transactions
    })