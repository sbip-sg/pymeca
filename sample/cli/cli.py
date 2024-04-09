import inspect


class MecaCLI:
    def __init__(self, actor):
        self.actor = actor
        all_methods = dir(actor)
        parent_methods = dir(actor.__class__.__base__)
        self.child_methods = []
        for method in all_methods:
            if method not in parent_methods and callable(getattr(actor, method)):
                self.child_methods.append(getattr(actor, method))

    async def run_func(self, func, args):
        if func is not None:
            is_coroutine = inspect.iscoroutinefunction(func)
            if is_coroutine:
                return await func(*args)
            else:
                return func(*args)
        else:
            return "Invalid method"

    def shutdown(self):
        pass

    def add_method(self, method):
        self.child_methods.append(method)

    async def start(self):
        try:
            while True:
                print()
                for i, method in enumerate(self.child_methods):
                    print(f"{i}. " + method.__name__)
                print("x. Exit")
                choice = input("Enter action: ").strip()

                if choice == "x" or choice == "X":
                    self.shutdown()
                    break

                if choice == "":
                    continue

                try:
                    print()
                    func = self.child_methods[int(choice)]
                    print(f"Running {func.__name__}")
                    params = inspect.signature(func).parameters
                    args = []
                    for param_name, param in params.items():
                        param_type = param.annotation
                        arg = param_type(input(f"Enter {param_name}: ").strip())
                        args.append(arg)
                except KeyboardInterrupt:
                    continue

                print()
                await self.run_func(func, args)
                input("Press Enter to continue...")

        except KeyboardInterrupt:
            self.shutdown()
            print("Exiting...")
            return
