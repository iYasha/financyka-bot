import datetime

from aiogram import types
from config import bot
from config import dp
from config import settings
from modules.operations.enums import OperationCreateCallback
from modules.operations.enums import OperationReceivedCallback
from modules.operations.schemas import Operation
from modules.operations.schemas import OperationUpdate
from modules.operations.services import OperationService

from sdk import utils
from sdk.exceptions.handler import error_handler_decorator


@dp.message_handler(regexp=settings.OPERATION_REGEX_PATTERN)
@error_handler_decorator
async def create_operation(message: types.Message) -> None:
    operation_data = OperationService.parse_operation(message.text, message.chat.id)
    if not operation_data:
        return

    operation: Operation = await OperationService.create_operation(operation_data)

    await bot.send_message(
        message.chat.id,
        text=await utils.get_operation_text(operation),
        parse_mode=settings.PARSE_MODE,
        reply_markup=await utils.get_operation_approved_markup(operation.id),
    )


@dp.callback_query_handler(
    lambda c: c.data and c.data.startswith(OperationCreateCallback.UNIQUE_PREFIX),
)
@error_handler_decorator
async def process_operation_create(callback_query: types.CallbackQuery) -> None:
    operation_text = callback_query.message.html_text
    if callback_query.data.startswith(OperationCreateCallback.CORRECT):
        operation_id = int(callback_query.data.replace(f'{OperationCreateCallback.CORRECT}_', ''))
        await OperationService.approve_operation(operation_id)
        operation_text = f'{operation_text}\n✅ Операция успешно создана'

    elif callback_query.data.startswith(OperationCreateCallback.NO):
        operation_id = int(callback_query.data.replace(f'{OperationCreateCallback.NO}_', ''))
        await OperationService.delete_operation(operation_id)
        operation_text = f'{operation_text}\n❌ Операция не создана'

    await bot.edit_message_text(
        text=operation_text,
        parse_mode=settings.PARSE_MODE,
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
    )


@dp.callback_query_handler(
    lambda c: c.data and c.data.startswith(OperationReceivedCallback.UNIQUE_PREFIX),
)
@error_handler_decorator
async def process_operation_received(callback_query: types.CallbackQuery) -> None:
    if callback_query.data.startswith(OperationReceivedCallback.PARTIAL):
        await callback_query.message.reply(
            text='<b>Чтобы указать полученную сумму - сделайте reply этого сообщения с указанием суммы</b>',
            parse_mode=settings.PARSE_MODE,
        )
        return

    operation_text = callback_query.message.html_text

    if callback_query.data.startswith(OperationReceivedCallback.FULL):
        operation_id = int(callback_query.data.replace(f'{OperationReceivedCallback.FULL}_', ''))
        await OperationService.approve_operation(operation_id)
        operation_text = f'{operation_text}\n✅ Операция успешно создана'
    elif callback_query.data.startswith(OperationReceivedCallback.NONE_RECEIVED):
        operation_text = f'{operation_text}\n❌ Сумма не получена'

    await bot.edit_message_text(
        text=operation_text,
        parse_mode=settings.PARSE_MODE,
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
    )


@dp.message_handler(
    lambda x: x.reply_to_message is not None
    and x.reply_to_message.reply_markup is not None
    and len(x.reply_to_message.reply_markup.inline_keyboard) > 0
    and len(x.reply_to_message.reply_markup.inline_keyboard[0]) > 0
    and x.reply_to_message.reply_markup.inline_keyboard[0][0].callback_data.startswith(
        OperationReceivedCallback.UNIQUE_PREFIX,
    ),
)
@error_handler_decorator
async def reply_received_handler(message: types.Message) -> None:
    if message.date >= datetime.datetime(
        year=message.date.year,
        month=message.date.month,
        day=message.date.day,
        hour=23,
        minute=59,
    ):
        await message.reply(
            text='<b>Вы уже не можете изменить полученную сумму</b>',
            parse_mode=settings.PARSE_MODE,
        )
    operation_id = int(
        message.reply_to_message.reply_markup.inline_keyboard[0][0].callback_data.replace(
            f'{OperationReceivedCallback.FULL}_',
            '',
        ),
    )
    if not message.text.strip().isdigit():
        await message.reply(text='<b>Нужно ввести число</b>', parse_mode=settings.PARSE_MODE)
    amount = int(message.text)
    if amount < 0:
        await message.reply(
            text='<b>Сумма должна быть больше 0</b>',
            parse_mode=settings.PARSE_MODE,
        )
    operation = await OperationService.get_operation(operation_id)
    received_amount = 0 or operation.received_amount
    await OperationService.update_operation(
        operation_id,
        OperationUpdate(received_amount=received_amount + amount),
    )
    received_amount_text = (
        f'⚠️ Получено {amount}/{operation.amount}'
        if operation.amount > amount
        else '✅ Сумма успешно сохранена'
    )
    await bot.edit_message_text(
        text=f'{message.reply_to_message.html_text}\n{received_amount_text}',
        parse_mode=settings.PARSE_MODE,
        chat_id=message.chat.id,
        message_id=message.reply_to_message.message_id,
    )