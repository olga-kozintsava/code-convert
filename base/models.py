from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
from django.utils import timezone


class Convert(models.Model):
    id_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    in_file = models.CharField(max_length=200)
    out_file = models.CharField(max_length=200)
    in_file_loc = models.IntegerField()
    in_file_size = models.IntegerField()
    in_tmstmp = models.DateTimeField(
        default=timezone.now,
        blank=False
    )
    out_tmstmp = models.DateTimeField(
        default=timezone.now,
        blank=False
    )

    def __str__(self):
        return f'{self.id} ,{self.id_user_id}, {self.id_user}  , {self.in_tmstmp}'

    class Meta:
        ordering = ['-in_tmstmp']


class Account(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='balance')
    balance = models.IntegerField(
        default=settings.START_BALANCE
    )

    def __str__(self):
        return str(self.balance)


class ConvertTransaction(models.Model):
    account = models.ForeignKey(
        'Account',
        on_delete=models.CASCADE,
        related_name='convert_transaction'
    )
    amount = models.IntegerField()
    date = models.DateTimeField(
        default=timezone.now,
        blank=False
    )
    id_convert = models.OneToOneField(
        'Convert',
        on_delete=models.CASCADE,
        related_name='amount'
    )


    def save(self, *args, **kwargs):
        self.account.balance -= self.amount
        self.account.save()
        super(ConvertTransaction, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.amount)


def create_user_account(sender, instance, created, **kwargs):
    if created:
        _, created = Account.objects.get_or_create(user=instance)


post_save.connect(create_user_account, sender=User)
