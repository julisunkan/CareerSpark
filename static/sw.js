// AI Resume Optimizer - Service Worker
const CACHE_NAME = 'resume-optimizer-v1.0.0';
const OFFLINE_URL = '/offline';

// Assets to cache on install
const STATIC_ASSETS = [
  '/',
  '/upload',
  '/static/css/custom.css',
  '/static/js/app.js',
  '/static/manifest.json',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png',
  'https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js'
];

// Install event - cache assets
self.addEventListener('install', event => {
  console.log('Service Worker: Installing...');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Service Worker: Caching static assets');
        return cache.addAll(STATIC_ASSETS.map(url => {
          return new Request(url, { cache: 'reload' });
        }));
      })
      .catch(error => {
        console.error('Service Worker: Cache failed', error);
      })
  );
  
  self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  console.log('Service Worker: Activating...');
  
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('Service Worker: Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  
  self.clients.claim();
});

// Fetch event - serve from cache or network
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }
  
  // Skip external URLs that aren't in our cache list
  if (!url.pathname.startsWith('/') && !STATIC_ASSETS.some(asset => asset === request.url)) {
    return;
  }
  
  event.respondWith(
    handleFetch(request)
  );
});

async function handleFetch(request) {
  const url = new URL(request.url);
  
  try {
    // For navigation requests (pages)
    if (request.mode === 'navigate') {
      return await handleNavigationRequest(request);
    }
    
    // For API calls
    if (url.pathname.startsWith('/api/') || 
        url.pathname.startsWith('/upload') || 
        url.pathname.startsWith('/download')) {
      return await handleApiRequest(request);
    }
    
    // For static assets
    return await handleStaticRequest(request);
    
  } catch (error) {
    console.error('Service Worker: Fetch failed', error);
    return await handleOfflineResponse(request);
  }
}

async function handleNavigationRequest(request) {
  try {
    // Try network first for navigation
    const networkResponse = await fetch(request);
    
    // Cache successful responses
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    // Network failed, try cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline page
    return await getOfflinePage();
  }
}

async function handleApiRequest(request) {
  try {
    // Always try network first for API calls
    const networkResponse = await fetch(request);
    return networkResponse;
  } catch (error) {
    // Return offline error for API calls
    return new Response(
      JSON.stringify({
        error: 'Offline',
        message: 'This feature requires an internet connection. Please check your connection and try again.'
      }),
      {
        status: 503,
        statusText: 'Service Unavailable',
        headers: {
          'Content-Type': 'application/json'
        }
      }
    );
  }
}

async function handleStaticRequest(request) {
  // Cache first strategy for static assets
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    
    // Cache successful responses
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    // Return a fallback for static assets
    return new Response('Asset unavailable offline', {
      status: 503,
      statusText: 'Service Unavailable'
    });
  }
}

async function handleOfflineResponse(request) {
  const url = new URL(request.url);
  
  // For navigation requests, show offline page
  if (request.mode === 'navigate') {
    return await getOfflinePage();
  }
  
  // For other requests, return cached version if available
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }
  
  // Return generic offline response
  return new Response('Content unavailable offline', {
    status: 503,
    statusText: 'Service Unavailable'
  });
}

async function getOfflinePage() {
  try {
    const cache = await caches.open(CACHE_NAME);
    const offlineResponse = await cache.match(OFFLINE_URL);
    if (offlineResponse) {
      return offlineResponse;
    }
  } catch (error) {
    console.error('Service Worker: Could not get offline page', error);
  }
  
  // Fallback offline HTML
  return new Response(`
    <!DOCTYPE html>
    <html lang="en" data-bs-theme="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Offline - AI Resume Optimizer</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                margin: 0;
                padding: 0;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                text-align: center;
            }
            .offline-container {
                max-width: 400px;
                padding: 2rem;
            }
            .offline-icon {
                font-size: 4rem;
                margin-bottom: 1rem;
                opacity: 0.8;
            }
            h1 {
                margin-bottom: 1rem;
                font-size: 1.5rem;
            }
            p {
                margin-bottom: 2rem;
                opacity: 0.9;
                line-height: 1.5;
            }
            .retry-btn {
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                color: white;
                padding: 0.75rem 1.5rem;
                border-radius: 0.5rem;
                text-decoration: none;
                display: inline-block;
                transition: all 0.3s ease;
            }
            .retry-btn:hover {
                background: rgba(255, 255, 255, 0.3);
                color: white;
                text-decoration: none;
            }
        </style>
    </head>
    <body>
        <div class="offline-container">
            <div class="offline-icon">📡</div>
            <h1>You're Offline</h1>
            <p>It looks like you've lost your internet connection. Some features may not be available until you're back online.</p>
            <a href="/" class="retry-btn" onclick="window.location.reload()">Try Again</a>
        </div>
    </body>
    </html>
  `, {
    headers: {
      'Content-Type': 'text/html'
    }
  });
}

// Background sync for uploading when back online
self.addEventListener('sync', event => {
  if (event.tag === 'background-sync') {
    event.waitUntil(handleBackgroundSync());
  }
});

async function handleBackgroundSync() {
  console.log('Service Worker: Background sync triggered');
  // Handle any queued uploads or data sync
}

// Push notification handling
self.addEventListener('push', event => {
  if (!event.data) return;
  
  const data = event.data.json();
  const options = {
    body: data.body,
    icon: '/static/icons/icon-192x192.png',
    badge: '/static/icons/icon-72x72.png',
    vibrate: [100, 50, 100],
    data: {
      url: data.url || '/'
    },
    actions: [
      {
        action: 'open',
        title: 'Open App'
      },
      {
        action: 'close',
        title: 'Close'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

// Notification click handling
self.addEventListener('notificationclick', event => {
  event.notification.close();
  
  if (event.action === 'open' || !event.action) {
    const url = event.notification.data?.url || '/';
    event.waitUntil(
      clients.openWindow(url)
    );
  }
});

console.log('Service Worker: Loaded successfully');