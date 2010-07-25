(function ($, dbg, app) {

    // ajax call to server for backend rpc functions.
    var req = function (fn_name, type, opts, cb, failure_cb) {
        if ((typeof(opts) === 'undefined') || $.isFunction(opts)) {
            cb = opts;
            opts = {};
        }
        if (typeof(cb) === 'undefined') { //cb skipped ?
            cb = dbg.log;
        }
        
        var len = opts.length;

        opts.action = fn_name;
        $.ajax({
            type: type,
            url: '/api',
            data: opts,
            success: function (resp, textStatus) {
                if (!resp.status 
                    || resp.status != 'ok' 
                    || textStatus != 'success') {
                    failure_cb(resp);
                    dbg.warn( 'RPC: failed', resp.status);
                    return;
                }
                cb(resp.result);
            },
            error: function (req, textStatus, err) {
                dbg.error( 'RPC: failed', req, textStatus, err);
            },
            dataType: 'json'
        });
    };

    req('get_rpc_method_list', 'GET', {},function (resp) {
        var posts = resp.methods.posts
        , gets = resp.methods.gets
        , rpc = {}
        , fn
        , i
        ;
            
        for (i=0; i<gets.length; i++) {
            fn = gets[i].fun;
            rpc[fn] = (function(fn) {
                return function () {
                    return req(fn, 'GET', arguments[0], arguments[1]);
                };
            }(fn));
        }
        
        for (i=0; i<posts.length; i++) {
            fn = posts[i].fun;
            rpc[fn] = (function(fn) {
                return function () {
                    return req(fn, 'POST', arguments[0], arguments[1]);
                };
            }(fn));
        }
        app.rpc = rpc;

        window.rpc = rpc;
        
        dbg.info('pubilshed api available message', app.rpc);
        // $.publish('/ph/api/available', PH_api);
    }, function (resp) {
        dbg.log('get_rpc_method_list failed', resp);
    });
    
})(jQuery, debug, YQL_hash, undefined);