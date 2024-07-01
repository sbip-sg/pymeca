class TestMecaUser:
    def test_send_task_on_blockchain(
        self,
        fill_setup,
        initial_task
    ):
        _, _, actors = fill_setup

        success, task_id = actors["user"].send_task_on_blockchain(
            ipfs_sha256=initial_task["ipfsSha256"],
            host_address=actors["host"].account.address,
            tower_address=actors["tower"].account.address,
            input_hash="0x" + "8" * 64,
        )

        assert success

        running_task = actors["user"].get_running_task(
            task_id=task_id
        )

        assert running_task["ipfsSha256"] == initial_task["ipfsSha256"]
        assert running_task["inputHash"] == "0x" + "8" * 64
        assert running_task["hostAddress"] == actors["host"].account.address
        assert running_task["towerAddress"] == actors["tower"].account.address
        assert running_task["owner"] == actors["user"].account.address
        assert running_task["size"] == initial_task["size"]
        assert (
            running_task["fee"]["scheduler"] ==
            actors["user"].get_scheduler_fee()
        )

        actors["host"].register_task_output(
            task_id=task_id,
            output_hash="0x" + "9" * 64
        )
        running_task = actors["user"].get_running_task(
            task_id=task_id
        )

        assert running_task["outputHash"] == "0x" + "9" * 64

        assert actors["user"].finish_task(
            task_id=task_id
        )

        running_task = actors["user"].get_running_task(
            task_id=task_id
        )

        assert running_task["ipfsSha256"] == "0x" + "0" * 64

        print(task_id)

    def test_get_towers_hosts_for_task(
        self,
        fill_setup,
        initial_task
    ):
        _, _, actors = fill_setup

        towers_hosts = actors["user"].get_towers_hosts_for_task(
            ipfs_sha256=initial_task["ipfsSha256"]
        )

        assert len(towers_hosts) == 1
        assert (
            towers_hosts[0]["hostAddress"] ==
            actors["host"].account.address
        )
        assert (
            towers_hosts[0]["towerAddress"] ==
            actors["tower"].account.address
        )


class TestMecaUserBadWorkflow:
    def test_expired_task_on_blockchain(
        self,
        fill_setup,
        initial_task
    ):
        _, _, actors = fill_setup

        success, task_id = actors["user"].send_task_on_blockchain(
            ipfs_sha256=initial_task["ipfsSha256"],
            host_address=actors["host"].account.address,
            tower_address=actors["tower"].account.address,
            input_hash="0x" + "8" * 64,
        )

        assert success

        success, _ = actors["user"].send_task_on_blockchain(
            ipfs_sha256=initial_task["ipfsSha256"],
            host_address=actors["host"].account.address,
            tower_address=actors["tower"].account.address,
            input_hash="0x" + "8" * 64,
        )

        assert success

        success, _ = actors["user"].send_task_on_blockchain(
            ipfs_sha256=initial_task["ipfsSha256"],
            host_address=actors["host"].account.address,
            tower_address=actors["tower"].account.address,
            input_hash="0x" + "8" * 64,
        )

        assert success

        running_task = actors["user"].get_running_task(
            task_id=task_id
        )

        assert running_task["ipfsSha256"] == initial_task["ipfsSha256"]
        assert running_task["inputHash"] == "0x" + "8" * 64
        assert running_task["hostAddress"] == actors["host"].account.address
        assert running_task["towerAddress"] == actors["tower"].account.address
        assert running_task["owner"] == actors["user"].account.address
        assert running_task["size"] == initial_task["size"]
        assert (
            running_task["fee"]["scheduler"] ==
            actors["user"].get_scheduler_fee()
        )

        assert actors["user"].finish_task(
            task_id=task_id
        )

        running_task = actors["user"].get_running_task(
            task_id=task_id
        )

        assert running_task["ipfsSha256"] == "0x" + "0" * 64

        print(task_id)

    def test_wrong_input_hash_task_on_blockchain(
        self,
        fill_setup,
        initial_task
    ):
        _, _, actors = fill_setup

        success, task_id = actors["user"].send_task_on_blockchain(
            ipfs_sha256=initial_task["ipfsSha256"],
            host_address=actors["host"].account.address,
            tower_address=actors["tower"].account.address,
            input_hash="0x" + "8" * 64,
        )

        assert success

        running_task = actors["user"].get_running_task(
            task_id=task_id
        )

        assert running_task["ipfsSha256"] == initial_task["ipfsSha256"]
        assert running_task["inputHash"] == "0x" + "8" * 64
        assert running_task["hostAddress"] == actors["host"].account.address
        assert running_task["towerAddress"] == actors["tower"].account.address
        assert running_task["owner"] == actors["user"].account.address
        assert running_task["size"] == initial_task["size"]
        assert (
            running_task["fee"]["scheduler"] ==
            actors["user"].get_scheduler_fee()
        )

        assert actors["host"].wrong_input_hash(
            task_id=task_id
        )

        running_task = actors["user"].get_running_task(
            task_id=task_id
        )

        assert running_task["ipfsSha256"] == "0x" + "0" * 64

        print(task_id)


class TestMecaUserTeeTask:
    def test_send_tee_task_on_blockchain(
        self,
        fill_setup,
        initial_tee_task
    ):
        _, _, actors = fill_setup

        success, task_id = actors["user"].send_task_on_blockchain(
            ipfs_sha256=initial_tee_task["ipfsSha256"],
            host_address=actors["host"].account.address,
            tower_address=actors["tower"].account.address,
            input_hash="0x" + "8" * 64,
        )

        assert success

        running_task = actors["user"].get_running_task(
            task_id=task_id
        )

        assert running_task["ipfsSha256"] == initial_tee_task["ipfsSha256"]
        assert running_task["inputHash"] == "0x" + "8" * 64
        assert running_task["hostAddress"] == actors["host"].account.address
        assert running_task["towerAddress"] == actors["tower"].account.address
        assert running_task["owner"] == actors["user"].account.address
        assert running_task["size"] == initial_tee_task["size"]
        assert (
            running_task["fee"]["scheduler"] ==
            actors["user"].get_scheduler_fee()
        )

        actors["host"].register_tee_public_key(
            task_id=task_id,
            tee_public_key=initial_tee_task["enclavePublicKey"]
        )

        tee_task = actors["user"].get_tee_task(
            task_id=task_id
        )

        assert (
            tee_task["enclavePublicKey"] ==
            initial_tee_task["enclavePublicKey"]
        )
        assert tee_task["encryptedInputHash"] == "0x" + "0" * 64

        actors["user"].register_tee_task_encrypted_input(
            task_id=task_id,
            hash_encrypted_input=initial_tee_task["encryptedInputHash"]
        )

        tee_task = actors["host"].get_tee_task(
            task_id=task_id
        )

        assert (
            tee_task["enclavePublicKey"] ==
            initial_tee_task["enclavePublicKey"]
        )
        assert (
            tee_task["encryptedInputHash"] ==
            initial_tee_task["encryptedInputHash"]
        )

        actors["host"].register_task_output(
            task_id=task_id,
            output_hash="0x" + "9" * 64
        )
        running_task = actors["user"].get_running_task(
            task_id=task_id
        )

        assert running_task["outputHash"] == "0x" + "9" * 64

        assert actors["user"].finish_task(
            task_id=task_id
        )

        running_task = actors["user"].get_running_task(
            task_id=task_id
        )

        assert running_task["ipfsSha256"] == "0x" + "0" * 64

        print(task_id)

    def test_get_towers_hosts_for_task(
        self,
        fill_setup,
        initial_tee_task
    ):
        _, _, actors = fill_setup

        towers_hosts = actors["user"].get_towers_hosts_for_task(
            ipfs_sha256=initial_tee_task["ipfsSha256"]
        )

        assert len(towers_hosts) == 1
        assert (
            towers_hosts[0]["hostAddress"] ==
            actors["host"].account.address
        )
        assert (
            towers_hosts[0]["towerAddress"] ==
            actors["tower"].account.address
        )
