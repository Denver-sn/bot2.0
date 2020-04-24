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

from haruka.modules.sql.locales_sql import switch_to_locale
from haruka.modules.tr_engine.strings import tld, LANGUAGES
from telegram.ext import CommandHandler
from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from haruka import dispatcher
from haruka.modules.tr_engine.list_locale import list_locales
from haruka.modules.sql.redis import get_lang_chat, chat_lang_set
from haruka.modules.helper_funcs.chat_status import user_admin
from telegram.ext import CallbackQueryHandler
import re

from haruka.modules.connection import connected


@user_admin
def locale(update, context):
    args = context.args
    chat = update.effective_chat
    message = update.effective_message
    if len(args) > 0:
        locale = args[0].lower()
        if locale == 'en-us':
            locale = 'en-US'
        if locale in ['en-uk', 'en-gb']:
            locale = 'en-GB'

        if locale in list_locales:
            if locale in LANGUAGES:
                chat_lang_set(chat.id, locale)
                switch_to_locale(chat.id, locale)
                if chat.type == "private":
                    message.reply_text(
                        tld(chat.id, 'language_switch_success_pm').format(
                            list_locales[locale]))
                else:
                    message.reply_text(
                        tld(chat.id, 'language_switch_success').format(
                            chat.title, list_locales[locale]))
            else:
                text = tld(chat.id, "language_not_supported").format(
                    list_locales[locale])
                text += "\n\n*Currently available languages:*\n"
                for lang in LANGUAGES:
                    locale = list_locales[lang]
                    text += "\n *{}* - `{}`".format(locale, lang)
                message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
        else:
            text = tld(chat.id, "language_code_not_valid")
            text += "\n\n*Currently available languages:*\n"
            for lang in LANGUAGES:
                locale = list_locales[lang]
                text += "\n *{}* - `{}`".format(locale, lang)
            message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    else:
        locale = get_lang_chat(chat.id)
        native_lang = list_locales[locale]
        message.reply_text(tld(chat.id,
                               "language_current_locale").format(native_lang),
                           parse_mode=ParseMode.MARKDOWN)


@user_admin
def locale_button(update, context):
    chat = update.effective_chat
    user = update.effective_user
    query = update.callback_query
    lang_match = re.findall(r"en-US|en-GB|id|ru", query.data)
    if lang_match:
        if lang_match[0]:
            chat_lang_set(chat.id, lang_match[0])
            switch_to_locale(chat.id, lang_match[0])
            query.answer(text=tld(chat.id, 'language_switch_success_pm').
                         format(list_locales[lang_match[0]]))
        else:
            query.answer(text="Error!", show_alert=True)

    locale = get_lang_chat(chat.id)
    curr_lang = list_locales[locale]

    text = tld(chat.id, "language_select_language")
    text += tld(chat.id, "language_user_language").format(curr_lang)

    conn = connected(update, context, chat, user.id, need_admin=False)

    if conn:
        try:
            chatlng = get_lang_chat(conn)
            chatlng = list_locales[chatlng]
            text += tld(chat.id, "language_chat_language").format(chatlng)
        except Exception:
            chatlng = "English (US)"

    text += tld(chat.id, "language_sel_user_lang")

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("English (US) 🇺🇸",
                                 callback_data="set_lang_en-US"),
            InlineKeyboardButton("English (UK) 🇬🇧",
                                 callback_data="set_lang_en-GB")
        ]] + [[
            InlineKeyboardButton("Indonesian 🇮🇩", callback_data="set_lang_id"),
            InlineKeyboardButton("Russian 🇷🇺", callback_data="set_lang_ru")
        ]] + [[
            InlineKeyboardButton(f"{tld(chat.id, 'btn_go_back')}",
                                 callback_data="bot_start")
        ]]))

    # query.message.delete()
    context.bot.answer_callback_query(query.id)


LOCALE_HANDLER = CommandHandler(["set_locale", "locale", "lang", "setlang"],
                                locale,
                                pass_args=True)
locale_handler = CallbackQueryHandler(locale_button, pattern="chng_lang")
set_locale_handler = CallbackQueryHandler(locale_button, pattern=r"set_lang_")

dispatcher.add_handler(LOCALE_HANDLER)
dispatcher.add_handler(locale_handler)
dispatcher.add_handler(set_locale_handler)
