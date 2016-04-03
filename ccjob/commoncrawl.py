from boto.s3.key import Key
import boto

from mrjob.job import MRJob
from warc import WARCFile
from urllib import url2pathname

from . gzipstream import GzipStreamFile

__all__ = ['CommonCrawl']


class CommonCrawl(MRJob):

    dataset = boto.connect_s3(anon=True).get_bucket('aws-publicdatasets')

    def process_record(self, body):
        raise NotImplementedError()

    def mapper(self, key, line):

        warcfile = WARCFile(fileobj=GzipStreamFile(Key(self.dataset, line)))

        for record in warcfile:
            for value in self.process_record(record):
                yield value, 1

            self.increment_counter('commoncrawl', 'processed_records', 1)

    def reducer(self, key, value):
        yield key, sum(value)
