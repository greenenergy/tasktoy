#!/usr/bin/env python3
"""
tasks.py - a module for exploring task levelling techniques.
"""

import datetime, random

class State(object):
    """
    Base class for Task states.
    """
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

class State_New(State):
    """
    Initial state for a Task
    """
    def __init__(self):
        super(State_New, self).__init__("New")

class State_Underway(State):
    """
    Task is actively being worked on
    """
    def __init__(self):
        super(State_Underway, self).__init__("Underway")

class State_Paused(State):
    """
    Task has been paused, possibly stalled due to outside conflict.
    """
    def __init__(self):
        super(State_Paused, self).__init__("Paused")

class State_Completed(State):
    """
    Task has been completed.
    """
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

    def weight(self):
        """
        Compute the 'available' weights for the resources managed by this task
        manager. I could recompute all the resources managed by the resource
        manager, but it's possible that the resource manager is managing
        resources for other projects, and we don't want to zero out those other
        project resources, so we'll do it just based on the tasks here.
        """
        all_resources = set()

        # Build up a unique set of resources so we're only setting their values
        # once.
        for t in self.tasks:
            if t.resource_group:
                for r in t.resource_group.resources:
                    all_resources.add(r)

        for r in all_resources:
            r.available_count = 0

            # This is probably incorrect actually, if we have resources
            # who are already assigned.
            r.assigned_count = 0

        for t in self.tasks:
            if t.resource_group:
                for r in t.resource_group.resources:
                    r.available_count += 1

        #for r in all_resources:
        #    print("%s: %s" % (r.name, r.available_count))

    def level(self):
        # Go through all the tasks. For each task, see if it has been assigned.
        # If not, then choose a resource to work on the task based on the
        # weights, then move on to the next task. If the task has prereqs, make
        # sure its starting point is no sooner than the end of the prereqs

        # We may need to iterate through the list of tasks a few times, so let's
        # use a running model.


        # So - for each task:
        #   1. Make sure it's unassigned and unallocated
        #   2. Choose a resource to work on it. The resources are sorted into
        #      priority order, so they should be checked in sorted order. Find
        #      the resource with next available block and choose him.
        #        - To do this, I'll need to be able to quickly get the time
        #          allocations per resource. So when a resource is assigned to
        #          a task, his "busy_until" value will be incremented by the
        #          tasks's start time plus the tasks's duration.

        for t in self.tasks:
            if t.hard_assigned_resources or t.auto_assigned_resources:
                continue

            t.satisfy()

            running = False

    def dot(self):

        print("digraph Dependencies {")
        # First, get a list of the resources involved.
        resource_set = set()

        for t in self.tasks:
            for r in t.hard_assigned_resources:
                resource_set.add(r)
            for r in t.auto_assigned_resources:
                resource_set.add(r)

        # Now, for each resource, define which tasks are in that resource's box
        for r in resource_set:
            print("subgraph cluster_%s {" % r.name)
            for t in r.assigned_tasks:
                print("%s;" % t.name)
            print("}")


        #print("rankdir=LR")
        for t in self.tasks:
            if t.milestone:
                print('{0} [shape=diamond, fillcolor=yellow, '\
                    'style="rounded,filled"]'.format(t.name))

        for t in self.tasks:
            t.dot()

        # Now do the soft dependencies
        for r in resource_set:
            if len(r.assigned_tasks) > 1:
                print("subgraph cluster_%s {" % r.name)
                print("%s [style=dotted];" %\
                    ("->".join([t.name for t in r.assigned_tasks])))
                print( "}")

        print("}")

    def __str__(self):
        r = []

        for t in self.tasks:
            r.append(str(t))

        return "\n".join(r)

class Resource(object):
    def __init__(self, name):
        self.name = name

        # The next_available_block is the next block of time this resource will
        # be available. This doesn't take calendars or work days into account,
        # this views work time linearly.
        self.next_available_block = 0

        # the available_count is how many tasks this resource is available for.
        # This is used purely for automatic levelling.
        self.available_count = 0

        # The assigned count is how many times this resource has been used.
        # For sorting, sort based on available+assigned, unless there are
        # multiple resources at the same value.
        # This is used purely for automatic levelling.
        self.assigned_count = 0

        self.assigned_tasks = []

    def assign(self, task):
        # This function is called from within the recursive satisfy() function.
        # Its safe to adjust the task start offset, because anything that
        # depends on this task will be resolved once we're finished updating
        # this one.
        task.auto_assigned_resources.append(self)
        self.assigned_count += 1

        # Choose the latest start date, based on the tasks initial start date
        # (based on its prerequisites) and the available time of the resource
        task.start_offset = max(task.start_offset, self.next_available_block)

        self.next_available_block = (task.duration + task.start_offset)
        #print("Resource: %s, task: %s, setting start to: %s, next avail: %s" % \
        #    (self.name, task.name, task.start_offset, self.next_available_block))

        self.assigned_tasks.append(task)

    def __lt__(self, other):
        # First - if the other is available sooner than self, then other wins.
        # If they have the same availability, then use the available/assigned
        # count calculation.

        if self.next_available_block < other.next_available_block:
            return True
        else:
            return (self.available_count+(self.assigned_count*2)) < \
                (other.available_count+(other.assigned_count*2))

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
        #self.resources = set()
        self.resources = {}

    def Resource(self, name):
        r = Resource(name)
        self.add(r)
        return r


    def add(self, r):
        #self.resources.add(r)
        self.resources[r.name] = r

    def print_chart_for(self, rname):
        res = self.resources[rname]
        for t in res.assigned_tasks:
            print(str(t))

    def __str__(self):
        r = []
        for res in self.resources.values:
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
        self.__resource_group = resource_group
        self.numworkers = numworkers

        # How many blocks until this task can start
        self.start_offset = 0

        # How long this task lasts. This is linear time, not taking into account
        # work days or calendars.
        self.duration = duration

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

    def satisfy(self):
        for p in self.prereqs:
            p.satisfy()

        if self.start_offset:
            return

        # Now choose the latest start date, based on each prereq's start_offset
        # plus their duration.

        latest = 0
        for p in self.prereqs:
            if p.start_offset + p.duration > latest:
                latest = p.start_offset + p.duration

        self.start_offset = latest

        if self.resource_group:
            if not (self.hard_assigned_resources or \
                    self.auto_assigned_resources):
                avail = sorted(self.resource_group.resources)
                res = avail[0]
                res.assign(self)


    @property
    def resource_group(self):
        return self.__resource_group

    @resource_group.setter
    def resource_group(self, rg):
        self.__resource_group = rg

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

    def avail(self, time, resource_group):
        """
        Build a set of resources who are available for a given time. It might
        make more sense to work based on a given restricted resource set.
        """
        a = set()
        for r in self.__resource_group.resources:
            pass
 
    def __str__(self):
        r = []
        #r.append("Task: %s" % self.name)
        #r.append("  State: %s" % self.state)
        #r.append("  Hard Resources: %s" % str(self.hard_assigned_resources))
        #r.append("  Auto Resources: %s" % str(self.auto_assigned_resources))
        #r.append("  Resource Group: %s" % str(self.resource_group))

        if self.auto_assigned_resources:
            r.append("{0:20}{1}{2} {3} [{4}]".format(
                self.name,
                self.start_offset*" ",
                str("*"*self.duration),
                ", ".join([str(x) for x in self.auto_assigned_resources]),
                str(self.__resource_group)
                ))
        else:
            r.append("{0:20}{1}{2} {3}".format(
            self.name,
            self.start_offset*" ",
            str("*"*self.duration),
                str(self.__resource_group)))


                #str(datetime.timedelta(minutes=self.duration*15)))
        return "\n".join(r)

    def dot(self):
        print("%s;" % self.name)

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
    print( "Please use the test module for testing")
    # -------------------
    # 1. Create a list of resources
    # 2. Create a list of tasks
    # 3. Create a resource group for each set of tasks
    # 4. Auto assign resources to tasks and level the tasks

    # So, first, go through all the tasks and weight each resource with how many
    # times they appear as available

#    for t in tasks:
#        for r in t.resource_group.resources:
#            r.available_count += 1
#
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

    #tm.level()

    #print(str(rm))

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


