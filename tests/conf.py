config = [
    {
        'type': 'elb',
        'name': 'test-elb',
        'metrics': [
            'Latency|Seconds',
            'RequestCount|Count'
        ],
        'child_metrics': [
            'test1',
            'test2',
            'test3||path:/data,year:2010'
        ]
    },
    {
        'type': 'block',
        'name': 'First Wave',
        'instances': [
            'i-0004',
            'i-0005',
            'i-pew'
        ],
        'metrics': [
            'test4',
            'test5',
            'test6||Path:/data',
        ]
    }
]