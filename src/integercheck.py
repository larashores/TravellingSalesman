import tkinter as tk


def int_validate(entry_widget, limits=(None, None)):
    """
    Validates an entry_widget so that only integers within a specified range may be entered

    Args:
        entry_widget: The tkinter.Entry widget to validate
        limits: The limits of the integer. It may be given as a (min, max) tuple or a
                   C-Type specifying whether it is signed and how many bits is is. Thus it may be
                   u8, s8, u16, s16, u32, or s32
    """
    if type(limits) == str:
        int_type = limits
        if int_type == 'u8':
            limits = [0, 256]
        elif int_type == 's8':
            limits = [-128, 127]
        elif int_type == 'u16':
            limits = [0, 65535]
        elif int_type == 's16':
            limits = [-32768, 32767]
        elif int_type == 'u32':
            limits = [0, 4294967295]
        elif int_type == 's32':
            limits = [-2147483648, 2147483647]
        else:
            raise Exception('Unknown type')
    num_str = entry_widget.get()
    current = None if (not _is_int(num_str)) else int(num_str)
    check = _NumberCheck(entry_widget, limits[0], limits[1], current=current)
    entry_widget.config(validate='all')
    entry_widget.config(validatecommand=check.vcmd)
    entry_widget.bind('<FocusOut>', lambda event: _validate(entry_widget, check))
    _validate(entry_widget, check)


def _is_int(num_str):
    """
    Returns whether or not a given string is an integer

    Args:
        num_str: The string to test

    Returns:
        Whether or not the string is an integer
    """
    try:
        int(num_str)
        return True
    except ValueError:
        return False


def _validate(entry, num_check):
    """
    Validates an entry so if there is invalid text in it it will be replaced by the last valid text

    Args:
        entry: The entry widget
        num_check: The NumberCheck instance that keeps track of the last valid number
    """
    try:
        int(entry.get())
    except ValueError:
        entry.delete(0, tk.END)
        entry.insert(0, str(num_check.last_valid))


class _NumberCheck:
    """
    Class used for validating entry widgets, self.vcmd is provided as the validatecommand
    """

    def __init__(self, parent, min_, max_, current):
        self.parent = parent
        self.low = min_
        self.high = max_
        self.vcmd = parent.register(self.in_integer_range), '%d', '%P'

        if _NumberCheck.in_range(0, min_, max_):
            self.last_valid = 0
        else:
            self.last_valid = min_
        if current is not None:
            self.last_valid = current

    def in_integer_range(self, _type, after_text):
        """
        Validates an entry to make sure the correct text is being inputted

        Args:
            type:        0 for deletion, 1 for insertion, -1 for focus in
            after_text:   The text that the entry will display if validated
        """

        if _type == '-1':
            if _is_int(after_text):
                self.last_valid = int(after_text)

        # Delete Action, always okay, if valid number save it
        if _type == '0':
            try:
                num = int(after_text)
                self.last_valid = num
            except ValueError:
                pass
            return True

        # Insert Action, okay based on ranges, if valid save num
        elif _type == '1':
            try:
                num = int(after_text)
            except ValueError:
                if self.can_be_negative() and after_text == '-':
                    return True
                return False
            if self.is_valid_range(num):
                self.last_valid = num
                return True
            return False
        return False

    def can_be_negative(self):
        """
        Tests whether this given entry widget can have a negative number

        Returns:
            Whether or not the entry can have a negative number
        """
        return (self.low is None) or (self.low < 0)

    def is_valid_range(self, num):
        """
        Tests whether the given number is valid for this entry widgets range

        Args:
            num: The number to range test

        Returns:
        Whether or not the number is in range
        """
        return _NumberCheck.in_range(num, self.low, self.high)

    @staticmethod
    def in_range(num, low, high):
        """
        Tests whether or not a number is within a specified range inclusive

        Args:
        num: The number to test if its in the range
        low: The minimum of the range
        high: The maximum of the range

        Returns:
            Whether or not the number is in the range
        """
        if (low is not None) and (num < low):
            return False
        if (high is not None) and (num > high):
            return False
        return True
