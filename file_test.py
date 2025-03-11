class Engine:
    def __init__(self, version):
        self.value = version

    def __set__(self, instance, value):
        if type(value) is Engine:
            self.value = value.value
        else:
            self.value = value


class Car:
    engine = Engine(1)

    def __init__(self, hook=None):
        self.hook = hook

    def drive(self):
        if self.hook:
            self.hook()
        print("DRIVE")


if __name__ == "__main__":
    car = Car()
    a = car.engine
    car.engine = Engine(2)
    car.engine = 2
