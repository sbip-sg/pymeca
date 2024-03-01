class TestMecaHostClean:
    def test_register_host(
        self,
        simple_setup,
        initial_host
    ):
        _, _, actors = simple_setup
        actors["host"].register(
            block_timeout_limit=initial_host["blockTimeoutLimit"],
            public_key=initial_host["eccPublicKey"],
            initial_deposit=initial_host["stake"]
        )

        assert actors["host"].get_host_block_timeout_limit(
            actors["host"].account.address
        ) == initial_host["blockTimeoutLimit"]
        assert actors["host"].get_host_public_key(
            actors["host"].account.address
        ) == initial_host["eccPublicKey"]
        assert actors["host"].get_host_stake(
            actors["host"].account.address
        ) == initial_host["stake"]

        new_public_key = "0x" + "3" * 128
        actors["host"].update_public_key(
            public_key=new_public_key
        )
        assert actors["host"].get_host_public_key(
            actors["host"].account.address
        ) == new_public_key

        new_block_timeout_limit = 20
        actors["host"].update_block_timeout_limit(
            new_block_timeout_limit=new_block_timeout_limit
        )
        assert actors["host"].get_host_block_timeout_limit(
            actors["host"].account.address
        ) == new_block_timeout_limit

        new_stake = 200
        actors["host"].increase_stake(
            amount=new_stake
        )
        assert actors["host"].get_host_stake(
            actors["host"].account.address
        ) == initial_host["stake"] + new_stake

        actors["host"].update_block_timeout_limit(
            new_block_timeout_limit=0
        )

        actors["host"].unregister()


class TestMecaHostRegister:
    def test_register_task(
        self,
        register_setup,
        initial_host_task
    ):
        _, _, actors = register_setup

        assert actors["host"].is_registered()

        host_tasks = actors["host"].get_my_tasks()

        assert len(host_tasks) == 0

        assert actors["host"].add_task(
            ipfs_sha256=initial_host_task["ipfsSha256"],
            block_timeout=initial_host_task["blockTimeout"],
            fee=initial_host_task["fee"]
        )

        host_tasks = actors["host"].get_my_tasks()

        assert len(host_tasks) == 1

        assert host_tasks[0]["ipfsSha256"] == initial_host_task["ipfsSha256"]
        assert (
            actors["host"].get_task_block_timeout(
                ipfs_sha256=initial_host_task["ipfsSha256"]
            ) == initial_host_task["blockTimeout"]
        )
        assert (
            actors["host"].get_task_fee(
                ipfs_sha256=initial_host_task["ipfsSha256"]
            ) == initial_host_task["fee"]
        )

        assert actors["host"].update_task_block_timeout(
            ipfs_sha256=initial_host_task["ipfsSha256"],
            block_timeout=initial_host_task["blockTimeout"] + 1
        )

        host_tasks = actors["host"].get_my_tasks()

        assert len(host_tasks) == 1

        assert host_tasks[0]["ipfsSha256"] == initial_host_task["ipfsSha256"]
        assert (
            actors["host"].get_task_block_timeout(
                ipfs_sha256=initial_host_task["ipfsSha256"]
            ) == (initial_host_task["blockTimeout"] + 1)
        )

        assert actors["host"].update_task_fee(
            ipfs_sha256=initial_host_task["ipfsSha256"],
            fee=initial_host_task["fee"] + 1
        )

        host_tasks = actors["host"].get_my_tasks()

        assert len(host_tasks) == 1

        assert host_tasks[0]["ipfsSha256"] == initial_host_task["ipfsSha256"]
        assert (
            actors["host"].get_task_fee(
                ipfs_sha256=initial_host_task["ipfsSha256"]
            ) == (initial_host_task["fee"] + 1)
        )

        assert actors["host"].delete_task(
            ipfs_sha256=initial_host_task["ipfsSha256"]
        )
