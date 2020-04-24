#    Haruka Aya (A telegram bot project)
#    Copyright (C) 2017-2019 Paul Larsen
#    Copyright (C) 2019-2020 Akito Mizukito (Haruka Network Development)

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.

#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

import html
from typing import List

from telegram import Update, Bot
from telegram.error import BadRequest
from telegram.ext import CommandHandler, Filters
from telegram.ext.dispatcher import run_async
from telegram.utils.helpers import mention_html

from haruka import dispatcher, LOGGER
from haruka.modules.helper_funcs.chat_status import user_admin, can_delete
from haruka.modules.log_channel import loggable
from haruka.modules.tr_engine.strings import tld


@run_async
@user_admin
@loggable
def purge(update, context) -> str:
    args = context.args
    msg = update.effective_message
    if msg.reply_to_message:
        user = update.effective_user
        chat = update.effective_chat
        if can_delete(chat, context.bot.id):
            message_id = msg.reply_to_message.message_id
            if args and args[0].isdigit():
                if int(args[0]) < int(1):
                    return

                delete_to = message_id + int(args[0])
            else:
                delete_to = msg.message_id - 1
            for m_id in range(delete_to, message_id - 1,
                              -1):  # Reverse iteration over message ids
                try:
                    context.bot.deleteMessage(chat.id, m_id)
                except BadRequest as err:
                    if err.message == "Message can't be deleted":
                        context.bot.send_message(
                            chat.id, tld(chat.id,
                                         "purge_msg_cant_del_too_old"))

                    elif err.message != "Message to delete not found":
                        LOGGER.exception("Error while purging chat messages.")

            try:
                msg.delete()
            except BadRequest as err:
                if err.message == "Message can't be deleted":
                    context.bot.send_message(
                        chat.id, tld(chat.id, "purge_msg_cant_del_too_old"))

                elif err.message != "Message to delete not found":
                    LOGGER.exception("Error while purging chat messages.")

            context.bot.send_message(chat.id, tld(chat.id,
                                                  "purge_msg_success"))
            return "<b>{}:</b>" \
                   "\n#PURGE" \
                   "\n<b>• Admin:</b> {}" \
                   "\nPurged <code>{}</code> messages.".format(html.escape(chat.title),
                                                               mention_html(user.id, user.first_name),
                                                               delete_to - message_id)

    else:
        msg.reply_text(tld(chat.id, "purge_invalid"))

    return ""


@run_async
@user_admin
@loggable
def del_message(update, context) -> str:
    chat = update.effective_chat
    if update.effective_message.reply_to_message:
        user = update.effective_user
        if can_delete(chat, context.bot.id):
            update.effective_message.reply_to_message.delete()
            update.effective_message.delete()
            return "<b>{}:</b>" \
                   "\n#DEL" \
                   "\n<b>• Admin:</b> {}" \
                   "\nMessage deleted.".format(html.escape(chat.title),
                                               mention_html(user.id, user.first_name))
    else:
        update.effective_message.reply_text(tld(chat.id, "purge_invalid2"))

    return ""


__help__ = True

DELETE_HANDLER = CommandHandler("del", del_message, filters=Filters.group)
PURGE_HANDLER = CommandHandler("purge",
                               purge,
                               filters=Filters.group,
                               pass_args=True)

dispatcher.add_handler(DELETE_HANDLER)
dispatcher.add_handler(PURGE_HANDLER)
