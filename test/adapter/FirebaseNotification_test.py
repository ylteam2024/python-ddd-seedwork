from dino_seedwork_be.implementation.adapter.messaging.firebase.FirebaseNotificationDrivingAdapter import \
    FirebaseNotificationDrivingAdapter
from dino_seedwork_be.utils.functional import unwrap_future_result_io


class TestFirebaseNotificationDrivingAdapter:
    async def test_push_to_a_device(self):
        adapter = FirebaseNotificationDrivingAdapter()
        test_user_token = "dUyLTpjhcrL99gwNtq-MVs:APA91bEvb5skJ4lLid1VLhqDXUa4OWXv96TOhpmRYBwfCY1BaUG75GTaUM33NNzweXutiFOBbIPsi9qf907N_phSY5kf4_S2XHnGRd1_Ze5F4gzXXd5jjWPphkEkgm3jBEDOFw_Rrqtl"
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
