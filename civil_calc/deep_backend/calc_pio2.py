class CalcPio2():
    def _sum(self, *a):
        return sum(a)


def main():
    my_sum_ob = CalcPio2()
    print(my_sum_ob._sum(1, 1, 1, 10))


if __name__ == '__main__':
    main()