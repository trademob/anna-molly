from sure import expect

from lib.modules.helper import extract_service_name, get_closest_datapoint, find_step_size, insert_missing_datapoints
from lib.modules.models import TimeSeriesTuple


class TestHelperMethods(object):
    def setUp(self):
        self.timeseries = [TimeSeriesTuple('_', 10, 1),
                           TimeSeriesTuple('_', 20, 1),
                           TimeSeriesTuple('_', 30, 1),
                           TimeSeriesTuple('_', 50, 1),
                           TimeSeriesTuple('_', 60, 1),
                           TimeSeriesTuple('_', 100, 1)]

    def test_extract_service_name(self):
        name = 'host.ip:0-0-0-0.service.count'
        expect(extract_service_name(name)).to.be.equal('0-0-0-0')

    def test_get_closest_datapoint(self):
        expect(get_closest_datapoint(self.timeseries, 10)).to.be.equal(TimeSeriesTuple('_', 10, 1))
        expect(get_closest_datapoint(self.timeseries, 40)).to.be.equal(TimeSeriesTuple('_', 30, 1))
        expect(get_closest_datapoint(self.timeseries, 99)).to.be.equal(TimeSeriesTuple('_', 100, 1))

    def test_find_step_size(self):
        expect(find_step_size(self.timeseries)).to.be.equal(10)

    def test_insert_missing_datapoints(self):
        default = 111
        step_size = 10
        exp = [TimeSeriesTuple('_', 10, 1),
               TimeSeriesTuple('_', 20, 1),
               TimeSeriesTuple('_', 30, 1),
               TimeSeriesTuple('_', 40, 111),
               TimeSeriesTuple('_', 50, 1),
               TimeSeriesTuple('_', 60, 1),
               TimeSeriesTuple('_', 70, 111),
               TimeSeriesTuple('_', 80, 111),
               TimeSeriesTuple('_', 90, 111),
               TimeSeriesTuple('_', 100, 1)]
        expect(insert_missing_datapoints(self.timeseries, default, step_size)).to.be.equal(exp)
