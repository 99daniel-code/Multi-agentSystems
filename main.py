from thespian.actors import *


class SimplestActor(Actor):
    """
    Объявляем класс – Простой актор, который в будущем станет агентом
    """

    def __init__(self):
        super().__init__()
        print('Создан новый актор')
        self.messages = []
        self.child_addresses = []

    def receiveMessage(self, msg, sender):
        print(f'Актор с адресом {self.myAddress} получил {msg} от {sender}')
        self.messages.append(msg)
        for message in self.messages:
            print(f'Актор с адресом {self.myAddress} ранее получал сообщение {message}')
        for child in self.child_addresses:
            print(f'Ретранслируем сообщение дочернему актору с адресом {child}')
            self.send(child, msg)
        if msg == 'CREATE_ACTOR':
            child_actor_address = self.createActor(SimplestActor)
            print(f'Создали нового актора, его адрес – {child_actor_address}')
            self.child_addresses.append(child_actor_address)


class NumberActor(Actor):
    def __init__(self):
        super().__init__()
        # В это поле будем сохранять полученное значение.
        self.value = 0

    def receiveMessage(self, msg, sender):
        print(f'Актор числа с адресом {self.myAddress} получил {msg} от {sender}')
        # Ожидаем, что в сообщении будет содержаться словарь
        # со значением числа, операцией и адресом актора-калькулятора.
        self.value = msg.get('init_value')
        operation = msg.get('operation')
        calculator_address = msg.get('calculator_address')
        # Отправляем калькулятору сообщение, состоящее из значения и операции.
        self.send(calculator_address, {'value': self.value, 'operation': operation})


class CalculatorActor(Actor):
    """
    Актор-калькулятор, расширенный в рамках самостоятельной работы.

    Помимо суммирования (операция 'SUM') актор умеет выполнять и другие
    арифметические действия: вычитание ('SUB'), умножение ('MUL')
    и деление ('DIV'). Тип операции передается вместе со значением
    в виде отдельного поля сообщения ('operation'), то есть реализован
    еще один тип сообщений и логика по его обработке, как и требуется
    в задании самостоятельной работы.
    """

    # Операция по умолчанию, если актору отправлено просто число
    # (для совместимости со сценарием из основного занятия).
    DEFAULT_OPERATION = 'SUM'

    def __init__(self):
        super().__init__()
        # Итоговый результат вычислений.
        self.result = None
        # История полученных сообщений (значение + операция).
        self.history = []

    def receiveMessage(self, msg, sender):
        # Если пришло "сырое" число (как в примере из занятия) -
        # считаем, что операция суммирования.
        if isinstance(msg, dict):
            value = msg.get('value')
            operation = msg.get('operation') or self.DEFAULT_OPERATION
        else:
            value = msg
            operation = self.DEFAULT_OPERATION

        self.history.append((value, operation))

        if self.result is None:
            # Первое полученное число становится начальным результатом.
            self.result = value
        elif operation == 'SUM':
            self.result += value
        elif operation == 'SUB':
            self.result -= value
        elif operation == 'MUL':
            self.result *= value
        elif operation == 'DIV':
            if value == 0:
                print(f'Актор-калькулятор с адресом {self.myAddress}: '
                      f'деление на ноль невозможно, значение {value} проигнорировано')
                self.history.pop()
                return
            self.result /= value
        else:
            print(f'Актор-калькулятор с адресом {self.myAddress}: '
                  f'неизвестная операция {operation}, значение {value} проигнорировано')
            self.history.pop()
            return

        print(f'Актор-калькулятор с адресом {self.myAddress} получил значение '
              f'{value} с операцией {operation} от {sender}, '
              f'текущий результат: {self.result}')


if __name__ == "__main__":
    # Создаем систему акторов, внутри которой они будут жить
    actorSystem = ActorSystem()

    print('________________________________')
    print('Запускаем работу системы с калькулятором (самостоятельная работа)')

    # Создаем актор-калькулятор, сохраняем его адрес.
    calculator_address = actorSystem.createActor(CalculatorActor)

    # 1) Первый актор-число задает начальное значение результата: 10
    number_agent_1 = actorSystem.createActor(NumberActor)
    init_message_1 = {'init_value': 10, 'operation': 'SUM', 'calculator_address': calculator_address}
    actorSystem.tell(number_agent_1, init_message_1)

    # 2) Прибавляем 5 (операция SUM): 10 + 5 = 15
    number_agent_2 = actorSystem.createActor(NumberActor)
    init_message_2 = {'init_value': 5, 'operation': 'SUM', 'calculator_address': calculator_address}
    actorSystem.tell(number_agent_2, init_message_2)

    # 3) Вычитаем 3 (операция SUB): 15 - 3 = 12
    number_agent_3 = actorSystem.createActor(NumberActor)
    init_message_3 = {'init_value': 3, 'operation': 'SUB', 'calculator_address': calculator_address}
    actorSystem.tell(number_agent_3, init_message_3)

    # 4) Умножаем на 4 (операция MUL): 12 * 4 = 48
    number_agent_4 = actorSystem.createActor(NumberActor)
    init_message_4 = {'init_value': 4, 'operation': 'MUL', 'calculator_address': calculator_address}
    actorSystem.tell(number_agent_4, init_message_4)

    # 5) Делим на 6 (операция DIV): 48 / 6 = 8.0
    number_agent_5 = actorSystem.createActor(NumberActor)
    init_message_5 = {'init_value': 6, 'operation': 'DIV', 'calculator_address': calculator_address}
    actorSystem.tell(number_agent_5, init_message_5)

    actorSystem.shutdown()
