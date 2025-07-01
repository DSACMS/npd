Cicadence for Primeval Privacy Math
=============================
Prime Lookback Picker i.e. Cicada Number Picker

Often, we want to pick a time period for analysis of patient data that intentionally does not line up with common time periods for analysis. 
This way, even if the same underlying patient data is used for a report, it is difficult to conduct a subtraction attack where one report can be used in 
conjunction with another report to provide precise details about one or small number of patients. 

The inspiration for this project comes from Cicadas which have (apparently) evolved an incubation period that is difficult for predators to sync with.
[https://en.wikipedia.org/wiki/Periodical_cicadas](https://en.wikipedia.org/wiki/Periodical_cicadas)


Goal
----
Pick a prime-number “look-back window” (in days) that collides *least often*
with a set of common analytics windows **within the next decade** (3 650 days).

A *collision* means:               day  %  LCM(p, base) == 0
where  p     = candidate prime look-back
       base  = one of the base windows

We *weight* collisions by density:
If a day is a multiple of *three* base windows, it contributes 3 to the score.

The script:

1.  Lists every prime `p` such that 10 < p < 90.
2.  Counts the *weighted* collisions for each `p` versus the base windows  
    [7, 10, 30, 60, 90, 365, 730, 1095, 1825, 3650].
3.  Prints the full table and highlights the prime with the **lowest score**.

Output example
--------------
    Prime with the lowest weighted collision score = 89 (score=10)

    Prime : Weighted collision score (lower is better)
     11 : 99
     13 : 84
     ...
     89 : 10

Interpretation
--------------
• Lower score → fewer “overlap events” where analytic windows
  hit the same day.

• `89` wins because its first overlaps with the densest windows
  (7 × 89, 10 × 89, 30 × 89) are so far out that only a handful
  fit inside 10 years.

Customization
-------------
* Change `BASE_WINDOWS` to suit your organisation’s standard KPI windows.
* Change `HORIZON_DAYS` (default 3650, 10 years) if you care about a shorter/longer
  planning horizon.


code runs on command line: 
```bash
>  python prime_lookback_picker.py
```

Results
--------------------
With the default parameters, the script produces: 

```
Prime : Weighted collision score (lower is better)

11 : 99
13 : 84
17 : 63
19 : 57
23 : 45
29 : 36
31 : 32
37 : 28
41 : 23
43 : 23
47 : 21
53 : 18
59 : 17
61 : 14
67 : 13
71 : 13
73 : 34
79 : 11
83 : 11
89 : 10
97 : 9
101 : 9
103 : 9
107 : 8
109 : 8
113 : 8
127 : 6
131 : 5
137 : 5
139 : 5
149 : 5
151 : 5
157 : 5
163 : 5
167 : 5
173 : 5
179 : 4
181 : 4
191 : 3
193 : 3
197 : 3
199 : 3
211 : 3
223 : 3
227 : 3
229 : 3
233 : 3
239 : 3
241 : 3
251 : 3
257 : 3
263 : 2
269 : 2
271 : 2
277 : 2
281 : 2
283 : 2
293 : 2
307 : 2
311 : 2
313 : 2
317 : 2
331 : 2
337 : 2
347 : 2
349 : 2
353 : 2
359 : 2
367 : 1
373 : 1
379 : 1
383 : 1
389 : 1
397 : 1
401 : 1
409 : 1
419 : 1
421 : 1
431 : 1
433 : 1
439 : 1
443 : 1
449 : 1
457 : 1
461 : 1
463 : 1
467 : 1
479 : 1
487 : 1
491 : 1
499 : 1
503 : 1
509 : 1
521 : 1
523 : 0
541 : 0
547 : 0
557 : 0
563 : 0
569 : 0
571 : 0
577 : 0
587 : 0
593 : 0
599 : 0
601 : 0
607 : 0
613 : 0
617 : 0
619 : 0
631 : 0
641 : 0
643 : 0
647 : 0
653 : 0
659 : 0
661 : 0
673 : 0
677 : 0
683 : 0
691 : 0
701 : 0
709 : 0
719 : 0
727 : 0
733 : 0
739 : 0
743 : 0
751 : 0
757 : 0
761 : 0
769 : 0
773 : 0
787 : 0
797 : 0
809 : 0
811 : 0
821 : 0
823 : 0
827 : 0
829 : 0
839 : 0
853 : 0
857 : 0
859 : 0
863 : 0
877 : 0
881 : 0
883 : 0
887 : 0
907 : 0
911 : 0
919 : 0
929 : 0
937 : 0
941 : 0
947 : 0
953 : 0
967 : 0
971 : 0
977 : 0
983 : 0
991 : 0
997 : 0
1009 : 0
1013 : 0
1019 : 0
1021 : 0
1031 : 0
1033 : 0
1039 : 0
1049 : 0
1051 : 0
1061 : 0
1063 : 0
1069 : 0
1087 : 0
1091 : 0
1093 : 0
1097 : 0

```

Discussion
----------------
For numbers under 100 days, 89 "wins" from a collision perspective, but time periods of 29 or 31 days might be the most useful... 

The next number to note is 523, which is less than two years, and is the first number with no collisions in a 10 year time-span. 

ymmv.

-ft

