from st2common.runners.base_action import Action
from st2tests.base import BaseActionTestCase
from mock import patch, Mock, MagicMock
from get_device_os import GetDeviceOSAction

from ddt import ddt, data, unpack

__all__ = [
    'GetDeviceOsActionTestCase'
]

@ddt
class GetDeviceOsActionTestCase(BaseActionTestCase):
    __test__ = True
    action_cls = GetDeviceOSAction

    def test_validResponse_returnsUptime(self):
        action = self.get_action_instance()
        host = "1.1.1.1"
        username = "user"
        password = "user"

        actionResult, details = action.run(host, username, password)
        self.assertEquals(actionResult, True)
