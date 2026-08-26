from engine.navigation import MapPoint, NavigationPlanner


def test_plan_route():
    planner = NavigationPlanner({
        "demo": [MapPoint("A", 0, 0), MapPoint("B", 100, 100)]
    })
    steps = planner.plan("demo")
    assert [step.target.name for step in steps] == ["A", "B"]


def test_reached():
    assert NavigationPlanner.reached(MapPoint("A", 10, 10), MapPoint("A", 20, 20), 20)
