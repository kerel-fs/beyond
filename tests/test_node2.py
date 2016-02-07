#!/usr/bin/env python
# -*- coding: utf-8 -*-

from space.utils.node import Node2

A = Node2('A')
B = Node2('B')
C = Node2('C')
D = Node2('D')
E = Node2('E')
F = Node2('F')
G = Node2('G')
H = Node2('H')
I = Node2('I')
J = Node2('J')
K = Node2('K')
L = Node2('L')
M = Node2('M')

#  F---E---L---M
#     / \
#    D---A
#  / |   |
# J  C---B
# |  |   |
# K  G   I
# |   \ /
# `----H


def test_path():

    A + B + C + D + A
    D + E + F
    E + A
    C + G + H + I + B
    D + J + K + H
    E + L + M

    assert A.path('B') == [A, B]
    assert A.path('C') == [A, B, C]
    assert A.path('D') == [A, D]
    assert A.path('E') == [A, E]
    assert A.path('F') == [A, E, F]
    assert A.path('G') == [A, B, C, G]
    assert A.path('H') == [A, B, I, H]
    assert A.path('I') == [A, B, I]
    assert A.path('J') == [A, D, J]
    assert A.path('K') == [A, D, J, K]
    assert A.path('L') == [A, E, L]
    assert A.path('M') == [A, E, L, M]


def test_steps():
    assert list(A.steps('B')) == [(A, B)]
    assert list(A.steps('C')) == [(A, B), (B, C)]
    assert list(A.steps('D')) == [(A, D)]
    assert list(A.steps('E')) == [(A, E)]
    assert list(A.steps('F')) == [(A, E), (E, F)]
    assert list(A.steps('G')) == [(A, B), (B, C), (C, G)]
    assert list(A.steps('H')) == [(A, B), (B, I), (I, H)]
    assert list(A.steps('I')) == [(A, B), (B, I)]
    assert list(A.steps('J')) == [(A, D), (D, J)]
    assert list(A.steps('K')) == [(A, D), (D, J), (J, K)]
    assert list(A.steps('L')) == [(A, E), (E, L)]
    assert list(A.steps('M')) == [(A, E), (E, L), (L, M)]