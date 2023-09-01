from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.on_call.models import OnCallStuff
from apps.on_call.models import OnCallTable
import copy


@receiver(post_delete, sender=OnCallStuff, dispatch_uid="delete_stuff_handler")
def delete_stuff_handler(sender, instance, **kwargs):
    on_call_table, tag = OnCallTable.objects.get_or_create(sequence_name='on_call')
    sequence = on_call_table.sequence
    sequence_tmp = copy.copy(sequence)
    for role in sequence:
        if role not in set([obj.on_call_role.role_name for obj in OnCallStuff.objects.all()]):
            sequence_tmp.pop(role)
    for role, number in sequence_tmp.items():
        if number + 1 > len(OnCallStuff.objects.filter(on_call_role__role_name=role)):
            sequence_tmp[role] = len(OnCallStuff.objects.filter(on_call_role__role_name=role)) - 1
    on_call_table.sequence = sequence_tmp
    on_call_table.save()


@receiver(post_save, sender=OnCallStuff, dispatch_uid="save_stuff_handler")
def save_stuff_handler(sender, instance, **kwargs):
    on_call_table, tag = OnCallTable.objects.get_or_create(sequence_name='on_call')
    sequence = on_call_table.sequence
    sequence_tmp = copy.copy(sequence)
    for role in set([obj.on_call_role.role_name for obj in OnCallStuff.objects.all()]):
        if role not in sequence:
            sequence_tmp[role] = 0
    on_call_table.sequence = sequence_tmp
    on_call_table.save()
