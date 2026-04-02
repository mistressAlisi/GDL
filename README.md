# GDL: GameDayLotto
GDL Is an advanced algorithm to compute possible sports statistics to generate wagering options 
for sportsbooks and all types of sports data statistic providers.

# Architecture:
GDL is broken down into several components, above all, the front end and the back end.

1. Algorithmic core and backend:

The GDL Backend is designed around a patented GPGPU compute algorithm that quickly uses vectors and matrix math to find possible solutions for given sport outcomes / wagering conditions.
The core algorithm exists in several versions inside the algos/ folder:
- core.py: The earliest, simple possible proof of concept using linear cpu compute to validate the acceptability of the algorithm.
- gdlgpucore_async.py: This is the recommended production algorithm. It leverages PyTorch and CUDA (or ROCm) to generate results as quickly as possible in an asynchronous manner so it can be used in asynchronous daemons.
- gpucore.py: An older version of the asynchronous core, left here for completeness.
- gpucore_max: This version of gpucore optimises for the maximum possible payout going beyond what the user specified for limits if solutions exist.
- gpucore_narrow: This version modified gpucore to only give the "narrow" range of options that the user specified. Unlike the max version, this one reliably stays within the bounds.

2. GDLDaemon:
- Using asychronous tools and methods, GDLDaemon creates a django/channels handler that implements websockets as a daemon to service incoming client requests to generate results. This mechanism relies on the gdlgpucore_async algorithm mentioned before, as it has been specifically optimised for this usage.

3. GDLProxy:
- The GDLProxy is a one-to-many pooling proxy based on FastAPI to pool many workers (GDLDaemons) to service multiple clients in a High availiabilty configuration. GDLProxy will always try to satisfy all requests - using any available registered daemon.

4. Grader:
- This is a checkout of our Grader submodule which is used to determine results from particular tickets/events (Winners/loosers)

5. DataEngine:
- DataEngine is a checkout of our DataEngine repository. DataEngine is responsible for sourcing, aggregating and pooling data from different data streams, normalising them into a structured data set that can be used to feed GDL with proper data.
- DataEngine runs asynchronously using daemons, just like GDL, but it is ualloy invoked on its own thread so the GIL and the complexities of Python process management does not create problems for either thread.
- DataEngine and GDL rely on PostgreSQL to exchange data.

6. licensemanager / matches / notifications / odds / outcomes / players / sports / wager / teams:
- These are the Django models for the ORM that are used all over the platform. 

7. Sportslotto net / sportslotto vip:
- These are landing page frontend pages written on Django+Boostrap+Jquery.

8. GDL_react_frontend:
- The React frontend for the application, relying on the gdl/ URI endpoint to link and interact with the user so they may use the application.
- This is built using vite into static/frontend inside the gdl folder for runtime operation using django and nginx/haproxy.

9. Management:
- Management includes Materialised views useful for creating dashboards and connecting to Grafana for observability.

10. Cashier:
- A checkout of react based Cashier, Cypress.
