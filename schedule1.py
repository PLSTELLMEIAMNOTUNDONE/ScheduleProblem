"""Example of a simple nurse scheduling problem."""
from ortools.sat.python import cp_model


def sch():
    lecture_rooms = 3
    casual_rooms = 3

    subjects = 11
    lessons = 30
    casual_groups = 9
    lecture_groups = 5
    subjectGroup = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0],
                    [2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0],
                    [1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0],
                    [1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
                    [1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
                    [1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
                    [1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0]
                    ]
    subGroup = {9: [0, 1, 2], 10: [3, 4, 5], 11: [6, 7, 8], 12: [0, 1, 2, 3], 13: [4, 5, 6, 7, 8]}  # sub
    unity = {}
    for g in range(casual_groups + lecture_groups):
        unity[g] = [g]
        for lg, v in subGroup.items():
            if g in v:
                unity[g].append(lg)
    print(unity)
    lecture_rooms_range = range(casual_rooms, lecture_rooms + casual_rooms)
    casual_rooms_range = range(casual_rooms)
    all_subjects = range(subjects)
    all_lessons = range(lessons)
    lecture_groups_range = range(casual_groups, lecture_groups + casual_groups)
    casual_groups_range = range(casual_groups)
    all_groups = range(lecture_groups + casual_groups)
    all_rooms = range(lecture_rooms + casual_rooms)

    class_sum = 0
    for s in all_subjects:
        for g in all_groups:
            class_sum += subjectGroup[s][g]
    print(class_sum)
    subjectGroupMap = {}
    for s in all_subjects:
        for g in all_groups:
            if subjectGroup[s][g] != 0:
                subjectGroupMap[(s, g)] = subjectGroup[s][g]
    roomsNames = {}
    subjectsNames = {}
    lessonsNames = {}
    groupsNames = {}

    for r in casual_rooms_range:
        roomsNames[r] = "cr" + str(r + 1)
    for r in lecture_rooms_range:
        roomsNames[r] = "lr" + str(r + 1)
    for s in all_subjects:
        subjectsNames[s] = "s" + str(s + 1)
    for l in all_lessons:
        lessonsNames[l] = "l" + str(l + 1)
    for g in casual_groups_range:
        groupsNames[g] = "g" + str(g + 1)
    for g in lecture_groups_range:
        groupsNames[g] = str([groupsNames[s] for s in subGroup[g]])

    schedule = {}

    model = cp_model.CpModel()
    for r in casual_rooms_range:
        for s in all_subjects:
            for l in all_lessons:
                for g in casual_groups_range:
                    schedule[(r, s, l, g)] = model.NewBoolVar(
                        f"sch_{roomsNames[r]}_{subjectsNames[s]}_{lessonsNames[l]}_{groupsNames[g]}")
    for r in lecture_rooms_range:
        for s in all_subjects:
            for l in all_lessons:
                for g in lecture_groups_range:
                    schedule[(r, s, l, g)] = model.NewBoolVar(
                        f"sch_{roomsNames[r]}_{subjectsNames[s]}_{lessonsNames[l]}_{groupsNames[g]}")

    for r in lecture_rooms_range:
        for l in all_lessons:
            model.AddAtMostOne(schedule[(r, s, l, g)] for s in all_subjects for g in lecture_groups_range)
    for r in casual_rooms_range:
        for l in all_lessons:
            model.AddAtMostOne(schedule[(r, s, l, g)] for s in all_subjects for g in casual_groups_range)
    # for s in all_subjects:
    #     for l in all_lessons:
    #         model.AddAtMostOne((schedule[(r, s, l, g)] for g in all_groups for r in
    #                             (casual_rooms_range if g in casual_groups_range else lecture_rooms_range)))
    for g in all_groups:
        for l in all_lessons:
            model.AddAtMostOne((schedule[(r, s, l, ug)] for ug in unity[g]
                                for s in all_subjects
                                for r in
                                (casual_rooms_range if ug in casual_groups_range else lecture_rooms_range)))

    for s in all_subjects:
        for g in all_groups:
            model.Add(sum(schedule[(r, s, l, g)]
                          for r in
                          (casual_rooms_range if g in casual_groups_range else lecture_rooms_range)
                          for l in all_lessons) == subjectGroup[s][g])
    # for k, v in subjectGroupMap.items():
    #     s, g = k
    #     model.Add(sum(
    #         schedule[(r, s, l, g)] for r in (casual_rooms_range if g in casual_groups_range else lecture_rooms_range)
    #         for l in all_lessons) == v)

    lessonToOptimize = []
    for l in all_lessons:
        if (l) % 5 > 0 and l != 0:
            lessonToOptimize.append(l)
    indix = {}
    for l in all_lessons:
        for g in casual_groups_range:
            if l % 5 <= 1:
                continue
            d = l // 5
            indix[(l, g)] = model.NewBoolVar(f"ind_{[l]}_{groupsNames[g]}")
            model.AddMaxEquality(indix[(l, g)], [schedule[(r, s, ll, ug)]
                                                 for ll in range(d * 5, l - 1)
                                                 for ug in unity[g]
                                                 for r in (
                                                     casual_rooms_range if ug in casual_groups_range else lecture_rooms_range)
                                                 for s in all_subjects])
            model.Add(indix[(l, g)] - sum(schedule[(r, s, l - 1, ug)]
                                          for ug in unity[g]
                                          for r in (
                                              casual_rooms_range if ug in casual_groups_range else lecture_rooms_range)
                                          for s in all_subjects)
                      + sum(schedule[(r, s, l, ug)]
                            for ug in unity[g]
                            for r in (casual_rooms_range if ug in casual_groups_range else lecture_rooms_range)
                            for s in all_subjects) <= 1)
    # z = sum(sum(schedule[(r, s, l, g)]
    #             for r in (casual_rooms_range if g in casual_groups_range else lecture_rooms_range)
    #             for s in all_subjects) * ((l + 0) % 5)
    #         for g in all_groups
    #         for l in lessonToOptimize)
    # model.Minimize(z)
    # model.Add(z <= 10)

    solver = cp_model.CpSolver()

    solver.parameters.enumerate_all_solutions = False
    status = solver.Solve(model)

    # print(solver.SolutionInfo())
    # print(solver.ResponseStats())

    if status == cp_model.FEASIBLE:
        print("ok")
    if status == cp_model.INFEASIBLE:
        print("not ok")

    print(status)
    result = {}
    sss = 0
    for k, v in schedule.items():
        r, s, l, g = k

        if solver.Value(v) and (s, g) in subjectGroupMap:
            result[k] = 1
            sss += 1

    ans = {}

    print(sss)
    # fix!
    def errors(schedule_inst):
        e = 0
        for g in casual_groups_range:
            for d in range(0, 6):
                last = -1
                start = False
                for l in range(0, 5):
                    exist = (any((r, s, (l + d * 5), g) in schedule_inst
                                 for r in casual_rooms_range
                                 for s in all_subjects)
                             or any((r, s, (l + d * 5), lg) in schedule_inst and g in subGroup[lg]
                                    for r in lecture_rooms_range
                                    for s in all_subjects
                                    for lg in lecture_groups_range))

                    if exist and start:
                        if last != l - 1:
                            for i in range(last + 1, l):
                                print("день " + str(d + 1) + " пара " + str(i + 1) + " грyппа " + groupsNames[g])
                                e += 1
                        last = l
                        continue
                    if exist:
                        start = True
                        last = l

        print("errors = " + str(e))

    for l in all_lessons:
        ans[l] = "расписания на день " + str((l // 5) + 1) + " пара № " + str((l % 5) + 1) + "\n"
    for k, v in result.items():
        r, s, l, g = k
        ans[l] += subjectsNames[s] + " проходит y грyппы " + groupsNames[g] + " в kабинете " + roomsNames[r] + "\n"
    for l in all_lessons:
        print(ans[l])
    errors(result)


if __name__ == "__main__":
    sch()
