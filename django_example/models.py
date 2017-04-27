# coding=utf8
import logging

from django.db import models

# Create your models here.

SOURCE = ['tele2', 'beeline', 'mts', 'megafon']

ops = zip(SOURCE, SOURCE)
import json

dirs = [[0, 'выход'], [1, 'вход']]
import urllib.request
from django.conf import settings


class SMS(models.Model):
    class Meta:
        verbose_name = 'СМС'
        verbose_name_plural = 'СМС'

    sphone = models.CharField(max_length=64, verbose_name='откуда', db_index=True)
    tphone = models.CharField(max_length=64, verbose_name='куда', db_index=True)
    message = models.TextField(verbose_name='текст сообщения')
    date = models.DateTimeField(auto_now_add=True, db_index=True)
    sended = models.BooleanField(default=False)
    op = models.CharField(choices=ops, max_length=16, verbose_name='оператор')
    direction = models.IntegerField(choices=dirs, default=0, verbose_name='направление')
    uuid = models.CharField(max_length=128, blank=True, null=True)