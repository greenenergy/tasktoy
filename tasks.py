#!/usr/bin/env python3

import datetime, random

class State(object):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

class State_New(State):
    def __init__(self):
        super(State_New, self).__init__("New")

class State_Underway(State):
    def __init__(self):
        super(State_Underway, self).__init__("Underway")

class State_Paused(State):
    def __init__(self):
        super(State_Paused, self).__init__("Paused")

class State_Completed(State):
    def __init__(self):
        super(State_Completed, self).__init__("Completed")

class TaskManager(object):
    def __init__(self):
        self.tasks = []

    def Task(self, name, duration=4, numworkers=1, resource_group=None,
        milestone=False):
        t = Task(name, duration, numworkers, resource_group, milestone)
        self.tasks.append(t)
        return t

    def dot(self):

        print("digraph Dependencies {")
        #print("rankdir=LR")
        for t in self.tasks:
            if t.milestone:
                print('{0} [shape=diamond, fillcolor=yellow, style="rounded,filled"]'.format(t.name))

        for t in self.tasks:
            t.dot()
        print("}")

    def __str__(self):
        r = []

        for t in self.tasks:
            r.append(str(t))

        return "\n".join(r)
class Resource(object):
    def __init__(self, name):
        self.name = name

        # the available_count is how many tasks this resource is available for.
        self.available_count = 0

        # The assigned count is how many times this resource has been used.
        # For sorting, sort based on available+assigned, unless there are
        # multiple resources at the same value
        self.assigned_count = 0

    def __lt__(self, other):
        return self.available_count < other.available_count

    def __cmp__(self, other):
        return cmp(self.available_count, other.available_count)

    def __str__(self):
        return "Name: %s, weight: %s" %  (self.name, self.available_count)

class ResourceGroup(object):
    def __init__(self, *resources):
        self.resources = set(resources)

    def __str__(self):
        return ", ".join([x.name for x in self.resources])
        #return str(self.resources)


class ResourceManager(object):
    def __init__(self):
        self.resources = set()

    def add(self, r):
        self.resources.add(r)

    def __str__(self):
        r = []
        for res in self.resources:
            r.append(str(res))
        return "\n".join(r)

class Task(object):
    s_new = State_New()
    s_underway = State_Underway()
    s_paused = State_Paused()
    s_completed = State_Completed()

    def __init__(self, name, duration=4, numworkers=1, resource_group=None,
        milestone=False):
        self.work_units = []	# work units applied so far
        self.name = name
        self.prereqs = []
        self.state = self.s_new
        self.resource_group = resource_group
        self.duration = duration
        self.numworkers = numworkers
        self.start_offset = 0
        self.milestone = milestone

        # hard assigned resources are those designated by the user, and are not
        # subject to change by the program.
        self.hard_assigned_resources = []

        # auto_assigned resources are those designated by the program and may be
        # changed at any time until the task has begun. Once the task has begun,
        # the resource becomes hard_assigned and must be changed manually if it
        # needs to be changed.
        self.auto_assigned_resources = []

        # A task may be waiting to start, underway, paused or completed.
        # Each state change could be accompanied by a comment. If a task is
        # paused because it is waiting for either another resource, the
        # completion of another task, or some 3rd party action, that should be
        # noted in a comment.

    def build_prereqs(self, other, sofar=set()):
        for x in other.prereqs:
            sofar.add(x)
            self.build_prereqs(x, sofar)

        return sofar

    def add_prereq(self, other):
        """ Add another task in as a prereq to this one """
        # First, see if we're already a prereq to other, thus causing a loop
        prereq_set = self.build_prereqs(other)
        if self in prereq_set:
            raise ValueError("Adding %s to %s creates a loop" %\
                (other.name, self.name))

        self.prereqs.append(other)

   # def assign(self):
   #     self.resource_group.sort()
   #     for x in range(self.numworkers):
   #         self.auto_assigned_resources.append(self.resource_group.resources[x])

    def avail(self, time, resource_group):
        """
        Build a set of resources who are available for a given time. It might
        make more sense to work based on a given restricted resource set.
        """
        a = set()
        for r in self.resource_group.resources:
            pass
 
    def __str__(self):
        r = []
        #r.append("Task: %s" % self.name)
        #r.append("  State: %s" % self.state)
        #r.append("  Hard Resources: %s" % str(self.hard_assigned_resources))
        #r.append("  Auto Resources: %s" % str(self.auto_assigned_resources))
        #r.append("  Resource Group: %s" % str(self.resource_group))

        if self.auto_assigned_resources:
            r.append("{0:20}{1}{2} {3}".format(
                self.name, self.start_offset*" ", str("-"*self.duration),
                str(self.auto_assigned_resources)))
        else:
            r.append("{0:20}{1}{2} {3}".format(self.name,
            self.start_offset*" ", str("-"*self.duration),
                str(self.resource_group)))


                #str(datetime.timedelta(minutes=self.duration*15)))
        return "\n".join(r)

    def dot(self):
        for x in self.prereqs:
            print(" %s -> %s;" % (x.name, self.name))

def flatten(tasks):
    # Because resources may be shared across multiple projects, when flattening
    # you need to take that into account.
    # I think actually that flattening a set of projects simultaneously would
    # probably be a good thing. This would allow us to maximize the efficiency
    # of resource allocation.
    # This won't always be possible, some people will have outside committments
    # that cannot be shifted, and this needs to be taken into account when
    # assigning them.

    current_time = 0
    running = True

    while running:
        needs_assignment = False
        for t in tasks:
            avail_resources = t.avail(current_time, t.resource_group)

        if not needs_assignment:
            running = False


if __name__ == '__main__':
    # -------------------
    # 1. Create a list of resources
    # 2. Create a list of tasks
    # 3. Create a resource group for each set of tasks
    # 4. Auto assign resources to tasks and level the tasks

    # So, first, go through all the tasks and weight each resource with how many
    # times they appear as available

    for t in tasks:
        for r in t.resource_group.resources:
            r.available_count += 1

    # -------------------
    # As we lay out tasks, we are at a "current time" point. Once all resources
    # are assigned for the current time point, we find the next nearest time
    # point when a resource becomes free - at the end of the shortest next task.
    # Then we begin looking at assignments again.
    #
    # So we start at CT=0, and go through each unassigned task.
    # When we get to an unassigned task, see if any of the resources assigned to
    # it are available at this time.
    # If so, take the set of available resources, sort in inverse
    # weight order, and choose the first.
    #
    # After every assignment, add one to the weight of the resource. The idea is
    # to bias the resource against being assigned again, until other less
    # assigned resources catch up. The only thing I would be afraid of would be
    # a resource who is available across many tasks not getting assigned to any
    # because his score is too high. Maybe it would be best to keep two tallys -
    # the number of available, and the number of assignments, and when sorting
    # in preference order, order first by (avail+assigned), and then within a
    # given group, order by assigned. This way, if someone has 7 availability
    # slots and 0 assigned slots, they will get chosen before someone with 5
    # availability slots and 2 assigned slots.

    flatten(tasks)

    print(str(rm))

    # If someone is working on something and they get blocked waiting for
    # something (another task or an outside supplier) then the task needs to be
    # marked as "blocked/paused" and the assigned tasks shuffled accordingly.
    # 
    # So the idea is that on your smartphone, you can always bring up a "What do
    # I do now" display, which is sensitive to task priorities and stalls.
    # Another thing I'd really like to try to take into account as much as
    # possible is the fact that switching mental contexts between projects is an
    # uncomfortable and time consuming process, so we'd want to minimize that
    # as much as possible. Probably something like, try to switch projects no
    # more often than once every 2 hours (8 work blocks).


