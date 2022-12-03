from abc import ABC, abstractmethod
import pickle
import re
from collections import UserDict
from datetime import datetime


class AbstractField(ABC):
    @property
    @abstractmethod
    def value(self):
        pass


class Field(ABC):
    def __init__(self, value) -> None:
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value) -> None:
        self._value = new_value


class Name(Field):
    def __init__(self, value: str) -> None:
        self.value = value

    @Field.value.setter
    def value(self, value: str) -> None:
        if not value:
            raise ValueError('The "name" field cannot be empty')
        if value in ADDRESS_BOOK:
            raise ValueError("Such a contact already exists")
        if value.isdigit():
            raise ValueError("The name cannot consist only of numbers")
        self._value = value


class Phone(Field):
    def __init__(self, value: str) -> None:
        self.value = value

    @Field.value.setter
    def value(self, value) -> None:
        MIN_LEN = 7
        MAX_LEN = 13
        phone = value.replace("+", "").replace("(", "").replace(")", "")
        if not (phone.isdigit() and (MAX_LEN >= len(phone) >= MIN_LEN)):
            raise ValueError
        self._value = [value]


class Birthday(Field):
    def __init__(self, value: datetime.date) -> None:
        self.value = value

    @Field.value.setter
    def value(self, value: datetime) -> None:
        today = datetime.now()
        if value > datetime.date(today):
            raise ValueError
        self._value = value


class Adress(Field):
    pass


class Email(Field):
    def __init__(self, value: str) -> None:
        self.value = value

    @Field.value.setter
    def value(self, value: str) -> None:
        result = re.findall(r"[a-zA-Z]{1,}[\w\.]{1,}@[a-zA-Z]{2,}.[a-zA-Z]{2,}", value)
        if not result:
            raise ValueError
        self._value = value


class Tag(Field):
    def __init__(self, value: str) -> None:
        self.value = value

    @Field.value.setter
    def value(self, value: str) -> None:
        if not value:
            tegs = f"NoneTag-{datetime.now().strftime('%m/%d/%Y, %H:%M')}"
        if " " not in value and value or "," in value:
            tegs = [tag.strip() for tag in value.split(",")]
            tegs.sort()
            tegs = str(tegs)

        if " " in value and "," not in value:
            print("Separated tags by commas")
            raise ValueError
        self._value = tegs


class NoteText(Field):
    pass


class Notification:
    def __init__(self, notes: NoteText, tags: Tag = None) -> None:
        self.tags = tags
        self.notes = notes


class AbstractRecord(ABC):
    def change_name(self, new_name: str) -> str:
        pass

    def change_phone(self, old_phone: str, new_phone: str) -> str:
        pass

    def change_birthday(self, new_birthday):
        pass

    def change_adress(self, new_address):
        pass

    def change_email(self, new_email):
        pass


class Record(AbstractRecord):
    def __init__(
        self,
        name: Name,
        phone: Phone,
        birthday: Birthday = None,
        adress: Adress = None,
        email: Email = None,
    ) -> None:
        self.name = name
        self.phone = phone
        self.birthday = birthday
        self.adress = adress
        self.email = email

    def change_name(self, new_name: str) -> str:

        new_name_obj = Name(new_name)

        new_record = Record(
            new_name_obj, self.phone, self.birthday, self.adress, self.email
        )

        del ADDRESS_BOOK[self.name.value]
        ADDRESS_BOOK.add_record(new_record)
        return "Name successfully changed."

    def change_phone(self, old_phone: str, new_phone: str) -> str:

        index = self.phone.value.index(old_phone)

        self.phone.value.pop(index)
        self.phone.value.append(new_phone)
        return f"Phone successfully changed from {old_phone} --> {new_phone}"

    def change_birthday(self, new_birthday):

        if len(new_birthday) == 3:
            try:
                person_birthday = datetime(
                    year=int(new_birthday[0]),
                    month=int(new_birthday[1]),
                    day=int(new_birthday[2]),
                ).date()

                self.birthday = Birthday(person_birthday)
                return "Birthday successfully changed."

            except ValueError:
                print("Birth date creation error")
        else:
            print("Invalid date")

    def change_adress(self, new_address):
        self.adress = Adress(new_address)
        return "Address successfully changed."

    def change_email(self, new_email):
        self.email = Email(new_email)
        return "Email successfully changed."


class AbstractRecord(ABC):
    @abstractmethod
    def write_contacts_to_file(self, value):
        pass


class AbstractLoader(ABC):
    @abstractmethod
    def read_contacts_from_file(self, value):
        pass


class RecordFile(AbstractRecord):
    def write_contacts_to_file(self, filename: str) -> None:
        with open(filename, "wb") as file:
            pickle.dump(self.data, file)


class LoadFile(AbstractLoader):
    def read_contacts_from_file(self, filename: str):
        try:
            with open(filename, "rb") as file:
                contacts_archive = pickle.load(file)
                return contacts_archive
        except FileNotFoundError:
            pass


class AdressBook(UserDict, RecordFile, LoadFile):
    def add_record(self, record: Record) -> None:
        self.data[record.name.value] = record


class NoteBook(UserDict, RecordFile, LoadFile):
    def add_note(self, notification: Notification) -> None:
        self.data[notification.tags.value] = notification


NOTE_BOOK = NoteBook()
ADDRESS_BOOK = AdressBook()
