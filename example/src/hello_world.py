from src import lib


def main() -> None:
    a: list[int] = lib.get_values()
    print(f'Hello world!')
    print(lib.get_values())


if __name__ == '__main__':
    main()
