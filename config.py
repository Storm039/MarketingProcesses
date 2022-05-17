from dotenv import dotenv_values


class Utils:

    @staticmethod
    def load_env():
        return dotenv_values('.env')

