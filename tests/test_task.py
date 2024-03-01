import pytest
import pymeca.task


@pytest.fixture(scope="class")
def other_task_developer(
    accounts,
    simple_setup
):
    w3, addresses, _ = simple_setup
    # make the user also a task developer
    return pymeca.task.MecaTaskDeveloper(
        w3=w3,
        private_key=accounts["meca_user"]["private_key"],
        dao_contract_address=addresses["dao_contract_address"]
    )


class TestMecaTaskDeveloperClean:
    def has_one_initial_task(
        self,
        task_developer,
        initial_task
    ):
        my_tasks = task_developer.get_my_tasks()
        assert len(my_tasks) == 1
        assert my_tasks[0]["ipfsSha256"] == initial_task["ipfsSha256"]
        assert my_tasks[0]["fee"] == initial_task["fee"]
        assert my_tasks[0]["computingType"] == initial_task["computingType"]
        assert my_tasks[0]["size"] == initial_task["size"]
        assert my_tasks[0]["owner"] == task_developer.account.address
        task_developer.delete_task(
            ipfs_sha256=initial_task["ipfsSha256"]
        )
        my_tasks = task_developer.get_my_tasks()
        assert len(my_tasks) == 0

    def test_register_task(
        self,
        simple_setup,
        initial_task
    ):
        _, _, actors = simple_setup
        actors["task_developer"].register_task(
            ipfs_sha256=initial_task["ipfsSha256"],
            fee=initial_task["fee"],
            computing_type=initial_task["computingType"],
            size=initial_task["size"]
        )
        self.has_one_initial_task(
            actors["task_developer"],
            initial_task
        )

    def test_register_task_cidv0(
        self,
        simple_setup,
        initial_task
    ):
        _, _, actors = simple_setup
        cidv0 = pymeca.utils.cidv1_object_from_sha256(
            initial_task["ipfsSha256"]
        ).to_v0()
        actors["task_developer"].register_task_cid(
            cid=str(cidv0),
            fee=initial_task["fee"],
            computing_type=initial_task["computingType"],
            size=initial_task["size"]
        )

        self.has_one_initial_task(
            actors["task_developer"],
            initial_task
        )

    def test_register_task_cidv1(
        self,
        simple_setup,
        initial_task
    ):
        _, _, actors = simple_setup
        cidv1 = pymeca.utils.cidv1_object_from_sha256(
            initial_task["ipfsSha256"]
        )
        actors["task_developer"].register_task_cid(
            cid=str(cidv1),
            fee=initial_task["fee"],
            computing_type=initial_task["computingType"],
            size=initial_task["size"]
        )

        self.has_one_initial_task(
            actors["task_developer"],
            initial_task
        )

    def test_update_task_fee(
        self,
        simple_setup,
        initial_task
    ):
        _, _, actors = simple_setup
        actors["task_developer"].register_task(
            ipfs_sha256=initial_task["ipfsSha256"],
            fee=initial_task["fee"],
            computing_type=initial_task["computingType"],
            size=initial_task["size"]
        )
        assert actors["task_developer"].update_task_fee(
            ipfs_sha256=initial_task["ipfsSha256"],
            fee=initial_task["fee"] + 1
        )
        my_tasks = actors["task_developer"].get_my_tasks()
        assert len(my_tasks) == 1
        assert my_tasks[0]["ipfsSha256"] == initial_task["ipfsSha256"]
        assert my_tasks[0]["fee"] == initial_task["fee"] + 1
        assert my_tasks[0]["computingType"] == initial_task["computingType"]
        assert my_tasks[0]["size"] == initial_task["size"]
        assert my_tasks[0]["owner"] == actors["task_developer"].account.address

        actors["task_developer"].delete_task(
            ipfs_sha256=initial_task["ipfsSha256"]
        )

    def test_update_task_size(
        self,
        simple_setup,
        initial_task
    ):
        _, _, actors = simple_setup
        actors["task_developer"].register_task(
            ipfs_sha256=initial_task["ipfsSha256"],
            fee=initial_task["fee"],
            computing_type=initial_task["computingType"],
            size=initial_task["size"]
        )
        assert actors["task_developer"].update_task_size(
            ipfs_sha256=initial_task["ipfsSha256"],
            size=initial_task["size"] + 1
        )
        my_tasks = actors["task_developer"].get_my_tasks()
        assert len(my_tasks) == 1
        assert my_tasks[0]["ipfsSha256"] == initial_task["ipfsSha256"]
        assert my_tasks[0]["fee"] == initial_task["fee"]
        assert my_tasks[0]["computingType"] == initial_task["computingType"]
        assert my_tasks[0]["size"] == initial_task["size"] + 1
        assert my_tasks[0]["owner"] == actors["task_developer"].account.address

        actors["task_developer"].delete_task(
            ipfs_sha256=initial_task["ipfsSha256"]
        )

    def test_update_task_owner(
        self,
        simple_setup,
        other_task_developer,
        initial_task
    ):
        _, _, actors = simple_setup
        actors["task_developer"].register_task(
            ipfs_sha256=initial_task["ipfsSha256"],
            fee=initial_task["fee"],
            computing_type=initial_task["computingType"],
            size=initial_task["size"]
        )
        my_tasks = other_task_developer.get_my_tasks()
        assert len(my_tasks) == 0
        assert actors["task_developer"].update_task_owner(
            ipfs_sha256=initial_task["ipfsSha256"],
            new_owner=other_task_developer.account.address
        )
        my_tasks = actors["task_developer"].get_my_tasks()
        assert len(my_tasks) == 0
        my_tasks = other_task_developer.get_my_tasks()
        assert len(my_tasks) == 1
        assert my_tasks[0]["ipfsSha256"] == initial_task["ipfsSha256"]
        assert my_tasks[0]["fee"] == initial_task["fee"]
        assert my_tasks[0]["computingType"] == initial_task["computingType"]
        assert my_tasks[0]["size"] == initial_task["size"]
        assert (
            my_tasks[0]["owner"] ==
            other_task_developer.account.address
        )

        other_task_developer.delete_task(
            ipfs_sha256=initial_task["ipfsSha256"]
        )
