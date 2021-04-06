// You can comment this JS out and the app will still work.
(function() {
    var app = {
      'routes': {

        'the-default-view': {
          'rendered': function() {
            console.log('view currently showing is "the-default-view"');
            app.preventScroll();
          }
        }, 

        'start': {
          'rendered': function() {
            console.log('view currently showing is "start"');
            app.preventScroll();
          }
        },
                
        'support': {
          'rendered': function() {
            console.log('view currently showing is "support"');
            app.preventScroll();
          }
        },          
                
        'mods': {
          'rendered': function() {
            console.log('view currently showing is "mods"');
            app.preventScroll();
          }
        },

        'plugins': {
          'rendered': function() {
            console.log('view currently showing is "plugins"');
            app.preventScroll();
          }
        },

        'maps': {
          'rendered': function() {
            console.log('view currently showing is "maps"');
            app.preventScroll();
          }
        },
        
        'command': {
          'rendered': function() {
            console.log('view currently showing is "command"');
            app.preventScroll();
          }
        },

        'gallery-new-year': {
          'rendered': function() {
            console.log('view currently showing is "gallery-new-year"');
            app.preventScroll();
          }
        },

        'gallery-hyper-loop': {
          'rendered': function() {
            console.log('view currently showing is "gallery-hyper-loop"');
            app.preventScroll();
          }
        },

        'gallery-pink-squad': {
          'rendered': function() {
            console.log('view currently showing is "gallery-pink-squad"');
            app.preventScroll();
          }
        },

        'resources': {
          'rendered': function() {
            console.log('view currently showing is "resources"');
            app.preventScroll();
          }
        },        
        
        'litematica': {
          'rendered': function() {
            console.log('view currently showing is "litematica"');
            app.preventScroll();
          }
        },  

        '#market': {
          'rendered': function() {
            console.log('view currently showing is "#market"');
            app.preventScroll();
          }
        },  


      },

      
      'default': 'the-default-view',
    'preventScroll': function() {
      document.querySelector('html').scrollTop = 0;
      document.querySelector('body').scrollTop = 0;
    },
    'routeChange': function() {
      app.routeID = location.hash.slice(1);
      app.route = app.routes[app.routeID];
      app.routeElem = document.getElementById(app.routeID);
      app.route.rendered();
    },
    'init': function() {
      window.addEventListener('hashchange', function() {
        app.routeChange();
      });
      if (!window.location.hash) {
        window.location.hash = app.default;
      } else {
        app.routeChange();
      }
    }
  };
  window.app = app;
})();

app.init();