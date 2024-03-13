import logging
import web3
import pymeca.pymeca
import pymeca.utils

logger = logging.getLogger(__name__)


class MecaTower(pymeca.pymeca.MecaActiveActor):
    def __init__(
        self,
        w3: web3.Web3,
        private_key: str,
        dao_contract_address: str
    ) -> None:
        r"""
        Init a tower.

        Args:
            w3 : Web3 instance.
            private_key : Private key of the tower
            dao_contract_address : DAO contract address.
        """
        super().__init__(
            w3=w3,
            private_key=private_key,
            dao_contract_address=dao_contract_address
        )

    def is_registered(
        self
    ) -> bool:
        r"""
        Check if the tower is registered on the blockchain.

        Returns:
            bool : True if the tower is registered.
        """
        return self.is_tower_registered(
            address=self.account.address
        )

    # getters functions
    def get_pending_hosts(
        self
    ) -> list:
        r"""
        Get pending hosts of the tower.

        Returns:
            list : List of pending hosts.
        """
        return self.get_tower_pending_hosts(
            tower_address=self.account.address
        )

    def get_my_hosts(
        self
    ) -> list:
        r"""
        Get all hosts of the tower.

        Returns:
            list : List of hosts.
        """
        return self.get_tower_hosts(
            tower_address=self.account.address
        )

    # setter functions
    # tower functions
    def register_tower(
        self,
        size_limit: int,
        public_connection: str,
        fee: int,
        fee_type: int,
        initial_deposit: int
    ) -> bool:
        r"""
        Register a new tower on the blockchain.

        Args:
            size_limit : Size limit of their storage.
            public_connection : Public connection.
            fee : Fee.
            fee_type : Fee type.
            initial_deposit : Initial deposit.

        Returns:
            bool : True if the tower was registered on the blockchain.
        """
        if initial_deposit < self.get_tower_initial_stake():
            raise ValueError(
                "The initial deposit is less than the minimum deposit"
            )

        transaction = self.get_tower_contract(
        ).functions.registerAsTower(
            sizeLimit=size_limit,
            publicConnection=public_connection,
            fee=fee,
            feeType=fee_type
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(
                self.account.address
            ),
            "value": initial_deposit
        })

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1

    def update_tower_size_limit(
        self,
        new_size_limit: int
    ) -> bool:
        r"""
        Update tower size limit on the blockchain.

        Args:
            new_size_limit : New size limit.

        Returns:
            bool : True if the size limit was updated successfully.
        """
        transaction = self.get_tower_contract(
        ).functions.updateSizeLimit(
            newSizeLimit=new_size_limit
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(
                self.account.address
            )
        })

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1

    def update_tower_public_connection(
        self,
        new_public_connection: str
    ) -> bool:
        r"""
        Update tower public connection on the blockchain.

        Args:
            new_public_connection : New public connection.

        Returns:
            bool : True if the public connection was updated successfully.
        """
        transaction = self.get_tower_contract(
        ).functions.updatePublicConnection(
            newPublicConnection=new_public_connection
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(
                self.account.address
            )
        })

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1

    def update_fee(
        self,
        new_fee_type: int,
        new_fee: int
    ) -> bool:
        r"""
        Update tower fee on the blockchain.

        Args:
            new_fee_type : New fee type.
            new_fee : New fee.

        Returns:
            bool : True if the fee was updated successfully.
        """
        transaction = self.get_tower_contract().functions.updateFee(
            newFee=new_fee,
            newFeeType=new_fee_type
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(
                self.account.address
            )
        })

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1

    def delete_tower(
        self
    ) -> bool:
        r"""
        Delete tower from the blockchain.

        Returns:
            bool : True if the tower was deleted successfully.
        """
        transaction = self.get_tower_contract(
        ).functions.deleteTower().build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(
                self.account.address
            )
        })

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1

    # host functions
    def accept_host(
        self,
        host_address: str
    ) -> bool:
        r"""
        Accept host on the blockchain from the pending list.

        Args:
            host_address : Host address.

        Returns:
            bool : True if the host was accepted successfully.
        """
        transaction = self.get_tower_contract(
        ).functions.acceptHost(
            hostAddress=host_address
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(
                self.account.address
            )
        })

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1

    def reject_host(
        self,
        host_address: str
    ) -> bool:
        r"""
        Reject host on the blockchain from the pending list.

        Args:
            host_address : Host address.

        Returns:
            bool : True if the host was rejected successfully.
        """
        transaction = self.get_tower_contract(
        ).functions.rejectHost(
            hostAddress=host_address
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(
                self.account.address
            )
        })

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1

    def delete_host(
        self,
        host_address: str
    ) -> bool:
        r"""
        Delete host from the blockchain from the tower hosts list.

        Args:
            host_address : Host address.

        Returns:
            bool : True if the host was deleted successfully.
        """
        transaction = self.get_tower_contract(
        ).functions.deleteHost(
            hostAddress=host_address
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(
                self.account.address
            )
        })

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1
