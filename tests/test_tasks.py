#!/usr/bin/env python3

import unittest, random


from tasks import Task, TaskManager, ResourceManager, Resource, ResourceGroup

class TaskTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_task_loops(self):
        """
        Make sure the system detects creating a dependency loop.
        """
        a = Task("a")
        b = Task("b")
        c = Task("c") 
        b.add_prereq(a)
        c.add_prereq(b)
        try:
            a.add_prereq(c)
            self.fail("Shouldn't have allowed a loop")
        except ValueError as e:
            pass

    def test_many_tasks(self):
        rm = ResourceManager()

        a = rm.Resource("A")    # General
        b = rm.Resource("B")    # General
        c = rm.Resource("C")    # General
        d = rm.Resource("D")    # Carpenter
        e = rm.Resource("E")    # Carpenter
        f = rm.Resource("F")    # Plumbing
        g = rm.Resource("G")    # Plumbing
        h = rm.Resource("H")    # Electrical
        i = rm.Resource("I")    # Electrical
        j = rm.Resource("J")    # Paint
        k = rm.Resource("K")    # Paint
        l = rm.Resource("L")    # Roofer
        m = rm.Resource("M")    # Glazer


        general = ResourceGroup( a,b,c )
        carpenter = ResourceGroup( d, e)
        plumber = ResourceGroup( f, g)
        electrical = ResourceGroup( h, i)
        paint = ResourceGroup( j, k)
        roofers = ResourceGroup( l )
        glazers = ResourceGroup( m )

        tm = TaskManager()

        foundation = tm.Task("foundation")
        foundation.resource_group = general
        basement = tm.Task("basement")
        basement.resource_group = general

        framing = tm.Task("framing")
        framing.resource_group = carpenter

        wiring = tm.Task("wiring")
        wiring.resource_group = electrical

        plumbing = tm.Task("plumbing")
        plumbing.resource_group = plumber

        flooring = tm.Task("flooring")
        flooring.resource_group = carpenter

        drywall = tm.Task("drywall")
        drywall.resource_group = carpenter

        exteriorwalls = tm.Task("exterior_walls")
        exteriorwalls.resource_group = carpenter

        interiorstructure = tm.Task("interiorstructure", milestone=True)
        exteriorstructure = tm.Task("exteriorstructure", milestone=True)
        
        framinginspection = tm.Task("framinginspection")
        plumbinginspection = tm.Task("plumbinginspection")
        wiringinspection = tm.Task("wiringinspection")

        fixtures = tm.Task("fixtures")
        interiorpaint = tm.Task("interior_paint")
        interiorpaint.resource_group = paint

        exteriorpaint = tm.Task("exterior_paint")
        exteriorpaint.resource_group = paint

        roofing = tm.Task("roofing")
        roofing.resource_group = roofers

        landscaping = tm.Task("landscaping")
        landscaping.resource_group = general

        gutters = tm.Task("gutters")
        gutters.resource_group = general
        gutters.add_prereq(roofing)

        glazing = tm.Task("glazing")
        glazing.resource_group = glazers
        glazing.add_prereq(framing)

        appliances = tm.Task("appliances")
        appliances.resource_group = general

        shingles = tm.Task("shingles")
        shingles.resource_group = roofers

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
        #tm.dot()
        #print(str(tm))
        #print("<>"*35)
        #rm.print_chart_for("E")
        #print("<>"*35)

    def test_resource_allocation_easy(self):
        """
        Easy test of resource allocation/levelling. 3 people (resources), 5
        tasks, 3 resource groups.
        """
        rm = ResourceManager()
        a = rm.Resource("A")
        b = rm.Resource("B")
        c = rm.Resource("C")
        #rm.add(a)
        #rm.add(b)
        #rm.add(c)

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

        #print "Laundry and Dinner"
        #print str(tm)

    def test_random_resource_allocation(self):
        rm = ResourceManager()

        reslist = "A B C D E F".split()

        res = [rm.Resource(x) for x in reslist]

        #for x in res:
        #    rm.add(x)

    #    numtasks = int(random.random()*20)
        numtasks =25 
        tasks = []
        tm = TaskManager()

        for x in range(numtasks):
            fg = list(res)
            random.shuffle(fg)
            group = fg[:int(random.random()*rm.num_resources)+1]
            #group = fg
            duration = int(random.random()*32)+1

            t = tm.Task(str(x),duration=duration,
                resource_group = ResourceGroup(*group))
            tasks.append(t)

        print "-------- Weighting ----------"
        tm.weight()
        tm.level()

        print str(tm)
        print("++++++++++++++++++++++++++++++")
        #for letter in reslist:
        #    print("[{0}]".format(letter))
        #    rm.print_chart_for(letter)
        for r in rm.resources:
            #print("[{0}] {1}".format(r.name, r.assigned_time))
            print("[{0}]".format(str(r)))
            rm.print_chart_for(r)

        print("++++++++++++++++++++++++++++++")
        #tm.dot()

