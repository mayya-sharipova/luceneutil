import os
import sys
import re
import time
import constants

r = re.compile(r'^(\d+): ([0-9\.]+) sec$')
r2 = re.compile(r'^Indexer: (\d+) docs... \(([0-9\.]+) msec\)$')
r3 = re.compile(r'^Indexer: (\d+) docs: ([0-9\.]+) sec')

def loadPoints(fileName):
  #print('load %s' % fileName)
  points = []
  with open(fileName, 'r') as f:
    for line in f.readlines():
      #print('line %s' % line)
      m = r.match(line.strip())
      if m is not None:
        points.append((int(m.group(1)), float(m.group(2))))
      m = r2.match(line.strip())
      if m is not None:
        #print('%s, %s' % (int(m.group(1)), m.group(2)))
        points.append((int(m.group(1)), float(m.group(2))/1000.))
      m = r3.search(line.strip())
      if m is not None:
        #print('%s, %s' % (int(m.group(1)), m.group(2)))
        points.append((int(m.group(1)), float(m.group(2))))
  return points

def gen():
  x = []
  w = x.append
  
  w('<html>')
  for prefix in ('logs',):
    #print('prefix %s' % prefix)
    if prefix == 'wiki':
      continue
    data = []
    root = '%s/results' % constants.BASE_DIR

    allTimes = set()
    for name in os.listdir(root):
      if name.startswith('results.%s' % prefix) and name.endswith('.txt'):
        #print('  %s' % name)
        label = name[(9+len(prefix)):-4].replace('.10gheap', '')
        points = loadPoints('%s/%s' % (root, name))
        byTime = {}
        for docs, sec in points:
          allTimes.add(sec)
          byTime[sec] = docs
        data.append((label, byTime))

    allTimes = list(allTimes)
    allTimes.sort()

    w('''
        <script type="text/javascript" src="https://www.google.com/jsapi"></script>
        <script type="text/javascript">
          google.load("visualization", "1", {packages:["corechart"]});
          google.setOnLoadCallback(drawChart);
          function drawChart() {
            var data = new google.visualization.DataTable();
            data.addColumn('number', 'Seconds');
            ''')

    for label, ign in data:
      w('data.addColumn("number", "%s");\n' % label)
    w('data.addRows([\n')
    lastSec = None
    for sec in allTimes:
      if lastSec is None or sec - lastSec >= 5.0:
        lastSec = sec
        row = ['%.1f' % sec]
        for label, byTime in data:
          value = byTime.get(sec)
          if value is None:
            value = 'null'
          else:
            value = '%.1f' % (value/1000.)
          row.append(value)
        w('[%s],\n' % ','.join(row))

    w('''
            ]);

            var options = {
              title: 'Bulk Indexing Performance',
              //legend: {position: 'bottom'},
              hAxis: {title: 'Seconds'},
              vAxis: {title: 'K Docs'},
              interpolateNulls: true,
            };

            var chart = new google.visualization.LineChart(document.getElementById('chart_div_%s'));
            chart.draw(data, options);
          }
        </script>
        <br><br>
        %s:
        <div id="chart_div_%s" style="width: 900px; height: 500px;"></div>
    ''' % (prefix, prefix, prefix))

  w('</html>')

  f = open('/x/tmp/results.html', 'w')
  f.write(''.join(x))
  f.close()

while True:
  #print('regen...')
  gen()
  time.sleep(1.0)
