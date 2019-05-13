var users = 
	[{	id: 'greg.garcia', 
		email: 'greg.garcia@bazaarvoice.com', 
		subscriptions: ['csttires', 'hasbro'] 
	},
	{	id: 'stephanie.gage', 
		email: 'stephanie.gage@bazaarvoice.com', 
		subscriptions: ['walmart', 'target']
	},
	{	id: 'brian.chang', 
		email: 'greg.garcia@bazaarvoice.com', 
		subscriptions: ['csttires', 'walmart']
	}];

var clients = [
	{
		id: 'csttires',
		pie_status: ['fail', {}],
		feed_status: ['stale', {
            latest_successful_import: '2019-05-13 09:26:03.478039',
            latest_failed_import: '2019-05-06 09:26:03.478039'
		}],
		display_status: ['pass', {}],
		pixel_status: ['pass', {}],
	},
	{
		id: 'hasbro',
		pie_status: ['pass', {}],
		feed_status: ['pass', {
		    latest_successful_import: '2019-05-13 09:26:03.478039',
		    latest_failed_import: '2019-05-06 09:26:03.478039'
		}],
		display_status: ['pass', {}],
		pixel_status: ['pass', {}],
	},
	{
		id: 'walmart',
		pie_status: ['fail', {}],
		feed_status: ['fail', {
		    latest_successful_import: '2019-05-13 09:26:03.478039',
		    latest_failed_import: '2019-05-06 09:26:03.478039'
		}],
		display_status: ['fail', {}],
		pixel_status: ['fail', {}],
	},
		{
		id: 'target',
		pie_status: ['pass', {}],
		feed_status: ['pass', {
		    latest_successful_import: '2019-05-13 09:26:03.478039',
		    latest_failed_import: '2019-05-06 09:26:03.478039'
		}],
		display_status: ['fail', {}],
		pixel_status: ['fail', {}],
	}]


