from src.seedwork.adapters.messaging.firebase.FirebaseNotificationDrivingAdapter import \
    FirebaseNotificationDrivingAdapter
from src.seedwork.utils.functional import unwrap_future_result_io


class TestFirebaseNotificationDrivingAdapter:
    async def test_push_to_a_device(self):
        adapter = FirebaseNotificationDrivingAdapter()
        test_user_token = "dItVm2ogWYAI1qoN8Ag6UU:APA91bEWPP9DFpHNCc_ZckOxlywPtcb13mDj-dVohn1EzD-h6Eo0mJoT9bdTBo_xfhREWPyHTi7zcKarzxZx9MSLOjqTqPkal2MbyJm1W1C1-G_bgAF_cdSYLJikAs0Jtl3H8eTQ5qcO"
        result_io = await adapter.push_to_device(
            {
                "package_id": "f8e12a8c-4aa2-4807-ae5c-0e9d730afb86",
                "package_offering_id": "614018ac-0dc3-4af6-9a76-c1598a39450b",
                "onchain_id": 52,
            },
            "BUY_PACKAGE_TIMEOUT",
            test_user_token,
        ).awaitable()

        result = unwrap_future_result_io(result_io)

        assert result is not None
