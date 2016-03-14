Common Crawl Data Extraction
============================

Extract data from common crawl using elastic map reduce

    Note: This project uses Python 2.7.11

CommonCrawlJob is a framework which wraps the ``MRJob`` hadoop library for streaming
analytics over internet scale data.

For more information on using `MRJob`_ framework.

Setup
-----

To develop locally, you will need to install the ``mrjob`` Hadoop
streaming framework library, and the ``boto`` library for accessing amazon cloud
public dataset resources.

Use pip to install these libraries.

.. code:: sh

    $ pip install CommonCrawlJob

Getting Started
---------------

To first get started, we are going to create a Google Analytics extractor. We will go from start to
finish in creating a Common Crawl extractor that uses regular expression capture groups to extract
google analytics tracker id's.

First let's create a file ``GoogleAnalytics.py``.

.. code:: sh

   $ touch GoogleAnalytics.py

Using a text editor, write to this file

.. code:: python

    import re

    from ccjob import CommonCrawl

    class GATagJob(CommonCrawl):

        def process_record(self, body):
            # Regular Expression for Google Analytics Tracker
            pat = re.compile(r"[\"\']UA-(\d+)-(\d)+[\'\"]")

            for match in pat.finditer(body):
                if match:
                    yield match.groups()[0]

            self.increment_counter('commoncrawl', 'processed_document', 1)


    if __name__ == '__main__':
        GATagJob.run()

Our ``GATagJob`` class has one method ``process_record`` taking in one argument containing
the body of a HTML file and yields the results matching our regular expression.

All common crawl jobs will generally obey this pattern.

Testing Locally
---------------

Run the Google Analytics extractor locally to test your script.

.. code:: sh

    $ python GoogleAnalytics.py -r local <(tail -n 1 data/latest.txt)


Region Configuration
--------------------

For best performance, you should launch the cluster in the same region
as your data. Currently data from `aws-publicdatasets`_ are stored in
``us-east-1``, which is where you want to point your EMR cluster.

Common Crawl Region
-------------------
:S3: US Standard
:EMR: US East (N. Virginia)
:API: ``us-east-1``

Create an Amazon EC2 Key Pair and PEM File
------------------------------------------

Amazon EMR uses an Amazon Elastic Compute Cloud (Amazon EC2) key pair
to ensure that you alone have access to the instances that you launch.

The PEM file associated with this key pair is required to ssh directly to the master node of the cluster.

To create an Amazon EC2 key pair:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
1. Go to the Amazon EC2 console
2. In the Navigation pane, click Key Pairs
3. On the Key Pairs page, click Create Key Pair
4. In the Create Key Pair dialog box, enter a name for your key pair, such as, mykeypair
5. Click Create
6. Save the resulting PEM file in a safe location

Configuring ``mrjob.conf``
--------------------------

Make sure to download an EC2 Key Pair ``pem`` file for your map reduce
job and add it to the ``ec2_key_pair`` and ``ec2_key_pair_file``
variables.

Make sure that the ``PEM`` file has permissions set properly by running

.. code:: sh

    $ chown 600 $MY_PEM_FILE

Download the latest version of python to send to your EMR instances.

.. code:: sh

   $ wget https://www.python.org/ftp/python/2.7.11/Python-2.7.11.tgz

Create a ``mrjob.conf`` file to set up your configuration parameters to match
that of AWS.

There is a default configuration template located at ``mrjob.conf.template`` that you can use.

.. code:: yaml

    runners:
      emr:
        aws_region: 'us-east-1'
        aws_access_key_id: <Your AWS_ACCESS_KEY_ID>
        aws_secret_access_key: <Your AWS_SECRET_ACCESS_KEY>
        cmdenv:
            AWS_ACCESS_KEY_ID: <Your AWS_ACCESS_KEY_ID>
            AWS_SECRET_ACCESS_KEY: <Your AWS_SECRET_ACCESS_KEY>
        ec2_key_pair: <Path to your PEM file>
        ec2_key_pair_file: <Name of the Key>
        ssh_tunnel_to_job_tracker: true
        ec2_instance_type: 'm1.xlarge'
        ec2_master_instance_type: 'm1.xlarge'
        emr_tags:
            name: '<Your Project Name>'
        num_ec2_instances: 12
        ami_version: '2.4.10'
        python_bin: python2.7
        interpreter: python2.7
        bootstrap_action:
            - s3://elasticmapreduce/bootstrap-actions/install-ganglia
        upload_files:
            - CommonCrawl.py
        bootstrap:
            - tar xfz Python-2.7.11.tgz#
            - cd Python-2.7.11
            - ./configure && make && sudo make install
            - sudo python2.7 get-pip.py#
            - sudo pip2 install --upgrade pip setuptools wheel
            - sudo pip2 install -r requirements.txt#

Run on Amazon Elastic MapReduce
-------------------------------

First copy the ``mrjob.conf.template`` into ``mrjob.conf``

Note: > Make sure to fill out the necessary AWS credentials with your
information

.. code:: sh

    $ python GoogleAnalytics.py -r emr \
                                --conf-path="mrjob.conf" \
                                --output-dir="s3n://$S3_OUTPUT_BUCKET" \
                               data/arcindex.txt


.. _MRJob: https://pythonhosted.org/mrjob/
.. _aws-publicdatasets: https://aws.amazon.com/public-data-sets/
