#!/usr/bin/env python3

import unittest, random


from tasks import Task, TaskManager, ResourceManager, Resource, ResourceGroup

class TaskTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_task_construction(self):
        t = Task("one")

    def test_task_loops(self):
        a = Task("a")
        b = Task("b")
        c = Task("c") 
        b.add_prereq(a)
        c.add_prereq(b)
        try:
            a.add_prereq(c)
            self.fail("Shouldn't have allowed a loop")
        except ValueError, e:
            pass

    def test_many_tasks(self):
        tm = TaskManager()
        foundation = tm.Task("foundation")
        basement = tm.Task("basement")
        framing = tm.Task("framing")
        wiring = tm.Task("wiring")
        plumbing = tm.Task("plumbing")
        flooring = tm.Task("flooring")
        drywall = tm.Task("drywall")
        exteriorwalls = tm.Task("exterior_walls")
        interiorstructure = tm.Task("interiorstructure", milestone=True)
        exteriorstructure = tm.Task("exteriorstructure", milestone=True)
        
        framinginspection = tm.Task("framinginspection")
        plumbinginspection = tm.Task("plumbinginspection")
        wiringinspection = tm.Task("wiringinspection")

        fixtures = tm.Task("fixtures")
        interiorpaint = tm.Task("interior_paint")
        exteriorpaint = tm.Task("exterior_paint")
        roofing = tm.Task("roofing")
        landscaping = tm.Task("landscaping")
        gutters = tm.Task("gutters")
        glazing = tm.Task("glazing")
        appliances = tm.Task("appliances")
        shingles = tm.Task("shingles")

        basement.add_prereq(foundation)
        framing.add_prereq(basement)
        framinginspection.add_prereq(framing)

        wiring.add_prereq(framinginspection)
        wiringinspection.add_prereq(wiring)

        plumbing.add_prereq(framinginspection)
        plumbinginspection.add_prereq(plumbing)

        flooring.add_prereq(framinginspection)

        drywall.add_prereq(plumbing)
        drywall.add_prereq(wiringinspection)

        exteriorwalls.add_prereq(framinginspection)
        exteriorpaint.add_prereq(exteriorwalls)

        roofing.add_prereq(framinginspection)
        shingles.add_prereq(roofing)


        interiorstructure.add_prereq(wiringinspection)
        interiorstructure.add_prereq(plumbinginspection)
        interiorstructure.add_prereq(flooring)
        interiorstructure.add_prereq(drywall)

        interiorpaint.add_prereq(interiorstructure)
        fixtures.add_prereq(interiorpaint)
        appliances.add_prereq(interiorpaint)

        landscaping.add_prereq(exteriorwalls)

        exteriorstructure.add_prereq(roofing)
        exteriorstructure.add_prereq(exteriorwalls)

        #print(str(tm))
        tm.weight()
        tm.level()
        tm.dot()

    def test_resource_allocation_easy(self):
        """
        Easy test of resource allocation/levelling. 3 people (resources), 5
        tasks, 3 resource groups.
        """
        rm = ResourceManager()
        a = Resource("A")
        b = Resource("B")
        c = Resource("C")
        rm.add(a)
        rm.add(b)
        rm.add(c)

        tm = TaskManager()
        dishes = tm.Task("dishes", duration=1)
        laundry_wash = tm.Task("laundry_wash", duration=1)
        laundry_dry = tm.Task("laundry_dry", duration=1)
        laundry_folding = tm.Task("laundry_folding", duration=2)
        dinner = tm.Task("dinner", duration=3)

        dinner.add_prereq(dishes)   # You need clean dishes before dinner
        laundry_dry.add_prereq(laundry_wash)
        laundry_folding.add_prereq(laundry_dry)

        rg1 = ResourceGroup( a,b )
        rg2 = ResourceGroup( b,c )
        rg3 = ResourceGroup( a,b,c )

        dishes.resource_group = rg1
        laundry_wash.resource_group = rg3
        laundry_dry.resource_group = rg3
        laundry_folding.resource_group = rg3
        dinner.resource_group = rg2

        tm.weight()
        tm.level()

        print "Laundry and Dinner"
        print str(tm)

    def test_random_resource_allocation(self):
        rm = ResourceManager()

        a = Resource("A")
        b = Resource("B")
        c = Resource("C")
        d = Resource("D")

        rm.add(a)
        rm.add(b)
        rm.add(c)
        rm.add(d)

    #    numtasks = int(random.random()*20)
        numtasks =15 
        tasks = []
        tm = TaskManager()

        for x in range(numtasks):
            fg = [a,b,c,d]
            random.shuffle(fg)
            #print("Fullgroup: %s" % ", ".join([str(x) for x in fg]))
            group = fg[:int(random.random()*3)+1]
            duration = int(random.random()*32)+1
            #print("Group: %s" % ", ".join([str(x) for x in group]))
            t = tm.Task(str(x),duration=duration,
                resource_group = ResourceGroup(*group))
            tasks.append(t)

        tm.weight()
        tm.level()

        print str(tm)
        print("***********************")
        for letter in "A B C D".split():
            print("[{0}]".format(letter))
            rm.print_chart_for(letter)

        print("***********************")
        tm.dot()

