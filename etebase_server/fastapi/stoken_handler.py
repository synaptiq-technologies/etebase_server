import typing as t

from django.db.models import QuerySet
from fastapi import status

from etebase_server.django.models import Stoken

from .exceptions import HttpError

# TODO missing stoken_annotation type
StokenAnnotation = t.Any


def get_stoken_obj(stoken: t.Optional[str]) -> t.Optional[Stoken]:
    if stoken:
        try:
            return Stoken.objects.get(uid=stoken)
        except Stoken.DoesNotExist:
            raise HttpError("bad_stoken", "Invalid stoken.", status_code=status.HTTP_400_BAD_REQUEST)

    return None


def filter_by_stoken(
    stoken: t.Optional[str], 
    queryset: QuerySet, 
    stoken_annotation: StokenAnnotation,
    reverse: bool = False
) -> t.Tuple[QuerySet, t.Optional[Stoken]]:
    stoken_rev = get_stoken_obj(stoken)

    queryset = queryset.annotate(max_stoken=stoken_annotation).order_by(
        "-max_stoken" if reverse else "max_stoken")

    if stoken_rev is not None:
        if reverse:
            queryset = queryset.filter(max_stoken__lt=stoken_rev.id)
        else:
            queryset = queryset.filter(max_stoken__gt=stoken_rev.id)

    return queryset, stoken_rev


def get_queryset_stoken(
    queryset: t.Iterable[t.Any], 
    reverse: bool = False
) -> t.Optional[Stoken]:
    id = None
    for row in queryset:
        rowmaxid = getattr(row, "max_stoken")
        if rowmaxid is None:
            continue 
        if id is None or (reverse and id > rowmaxid) or (not reverse and id < rowmaxid):
            id = rowmaxid
    new_stoken = Stoken.objects.get(id=id) if id is not None else None

    return new_stoken or None


def filter_by_stoken_and_limit(
    stoken: t.Optional[str], 
    limit: int, 
    queryset: QuerySet, 
    stoken_annotation: StokenAnnotation,
    reverse: bool = False
) -> t.Tuple[list, t.Optional[Stoken], bool]:

    queryset, stoken_rev = filter_by_stoken(
        stoken=stoken, queryset=queryset, stoken_annotation=stoken_annotation, reverse=reverse)

    result = list(queryset[: limit + 1])
    if len(result) < limit + 1:
        done = True
    else:
        done = False
        result = result[:-1]

    new_stoken_obj = get_queryset_stoken(result, reverse) or stoken_rev

    return result, new_stoken_obj, done
