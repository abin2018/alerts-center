from django.db import models


class OnCallRole(models.Model):
    role_name = models.CharField(max_length=50, unique=True, verbose_name='角色名称')
    role_desc = models.CharField(max_length=50, blank=True, verbose_name='角色描述')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '值班角色'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.role_name


class OnCallStuff(models.Model):
    stuff_name = models.CharField(max_length=50, verbose_name='姓名')
    on_call_role = models.ForeignKey(OnCallRole, on_delete=models.CASCADE, related_name='on_call_stuff',
                                     verbose_name='值班角色')
    stuff_phone_number = models.CharField(max_length=11, unique=True, verbose_name='手机号码')
    stuff_email = models.EmailField(unique=True, verbose_name='邮箱')
    rank_number = models.SmallIntegerField(default=0, verbose_name='次序')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '值班人员'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.stuff_name


class OnCallTable(models.Model):
    sequence_name = models.CharField(max_length=50, default='on_call', verbose_name='序列名称')
    sequence = models.JSONField(default=dict, verbose_name='序列')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '值班表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.sequence_name
