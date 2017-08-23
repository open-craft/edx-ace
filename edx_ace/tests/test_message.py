# lint-amnesty, pylint: disable=missing-docstring
from functools import partial
import six
from unittest import TestCase  # lint-amnesty, pylint: disable=wrong-import-order
from edx_ace.recipient import Recipient
from edx_ace.message import Message, MessageType
from edx_ace.utils.date import get_current_time
from hypothesis import strategies as st
from hypothesis import given, example  # lint-amnesty, pylint: disable=unused-import
from hypothesis.extra.pytz import timezones


context_values = st.one_of(st.text(), st.booleans(), st.floats(allow_nan=False))
dates = st.datetimes(timezones=st.none() | timezones())

msg = st.builds(
    Message,
    app_label=st.text(),
    name=st.text(),
    expiration_time=dates,
    context=st.dictionaries(
        st.text(),
        context_values,
    ),
    recipient=st.builds(
        Recipient,
        username=st.text(),
    ),
)

class TestMessage(TestCase):  # lint-amnesty, pylint: disable=missing-docstring
    def setUp(self):
        self.msg_kwargs = {
            'app_label': u'test_app_label',
            'name': u'test_message',
            'expiration_time': get_current_time(),
            'context': {
                u'key1': u'value1',
                u'key2': u'value2',
            },
            'recipient': Recipient(
                username=u'me',
            )
        }

    def test_basic(self):
        msg = Message(**self.msg_kwargs)  # lint-amnesty, pylint: disable=redefined-outer-name
        for key in self.msg_kwargs:
            self.assertEquals(getattr(msg, key), self.msg_kwargs.get(key))  # lint-amnesty, pylint: disable=deprecated-method
        self.assertIsNotNone(msg.uuid)

    def test_serialization(self):
        msg = Message(**self.msg_kwargs)  # lint-amnesty, pylint: disable=redefined-outer-name
        string_value = six.text_type(msg)
        resurrected_msg = Message.from_string(string_value)
        self.assertEquals(msg, resurrected_msg)  # lint-amnesty, pylint: disable=deprecated-method

    @given(msg)
    def test_serialization_round_trip(self, message):
        serialized = six.text_type(message)
        parsed = Message.from_string(serialized)
        self.assertEquals(message, parsed)  # lint-amnesty, pylint: disable=deprecated-method


def mk_message_type(name, app_label):
    class CustomType(MessageType):
        NAME = name
        APP_LABEL = app_label
    return CustomType


msg_type = st.builds(
    mk_message_type,
    name=st.one_of(st.none(), st.text()),
    app_label=st.text(),
).flatmap(
    partial(
        st.builds,
        expiration_time=dates,
        context=st.dictionaries(
            st.text(),
            context_values,
        ),
    )
)


class TestMessageTypes(TestCase):
    @given(msg_type)
    def test_serialization_roundtrip(self, msg_type):  # lint-amnesty, pylint: disable=redefined-outer-name
        serialized = six.text_type(msg_type)
        print(serialized)
        parsed = MessageType.from_string(serialized)
        self.assertEquals(msg_type, parsed)  # lint-amnesty, pylint: disable=deprecated-method, missing-final-newline