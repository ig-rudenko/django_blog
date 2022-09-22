from django.core.paginator import Paginator
from django.db import connection
from rest_framework.pagination import PageNumberPagination
from django.core.cache import cache


class CachedPaginator(Paginator):
    def __init__(self, object_list, per_page, orphans=0, allow_empty_first_page=True, cache_name=None):
        super().__init__(object_list, per_page, orphans, allow_empty_first_page)
        self.cache_name = cache_name
        self._count = None

    @property
    def count(self):
        # print(f'{self.cache_name=}')

        if not self.cache_name:  # Если имя кеша не было передано, то работаем, как с обычным пагинатором
            if not self._count:
                self._count = super(CachedPaginator, self).count
            return self._count

        # Работа с кешем
        c = cache.get(self.cache_name)  # Получаем из кеша запись
        # print('cache:', c)
        if c is None:  # Если в кеше нет записи
            c = super(CachedPaginator, self).count
            cache.set(self.cache_name, c)

        return c


class LargeTablePaginator(Paginator):
    """Переопределяет метод подсчета, чтобы получить оценку вместо фактического подсчета, если он не отфильтрован."""
    _count = None  # Кэш кол-ва записей, по умолчанию значение отсутствует
    _limit = 10_000  # Предел для быстрого поиска
    _standard_count = False  # Точный поиск уже был сделан?

    def validate_number(self, number):
        try:
            number = int(number)
        except (TypeError, ValueError):
            number = 1

        # Если значение подошло к 0.9 от всех записей, то включаем точный подсчет
        if not self._standard_count and (number * self.per_page) > self.count * 0.9:
            self._standard_count = True
            self._count = self.object_list.count()

        if number < 1:
            number = 1
        elif number > self.num_pages:
            if number == 1 and self.allow_empty_first_page:
                pass
            else:
                number = self.num_pages
        return number

    @property
    def count(self):
        """Если быстрый подсчет дал менее 10 000 записей, то возвращает общее количество объектов"""
        if self._count is None:
            try:
                estimate = 0
                if not self.object_list.query.where:
                    try:
                        cursor = connection.cursor()
                        cursor.execute(
                            'SELECT reltuples FROM pg_class WHERE relname = %s',
                            [self.object_list.query.model._meta.db_table])
                        estimate = int(cursor.fetchone()[0])
                    except:
                        pass
                if estimate < self._limit:
                    # Записи не превысили лимит для точного поиска, запускаем его
                    self._standard_count = True
                    self._count = self.object_list.count()
                else:
                    self._count = estimate
            except (AttributeError, TypeError):
                # AttributeError if object_list has no count() method.
                # TypeError if object_list.count() requires arguments
                # (i.e. is of type list).
                self._count = len(self.object_list)

        return self._count


class LargeTablePaginatorAPI(PageNumberPagination):
    django_paginator_class = LargeTablePaginator
