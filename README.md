# susbot-wenglab (fork of susbot)
- [x] Fix dependency issues (pyslurm requires SLURM shared libraries and header files)
- [x] Refactor user conversion from Slack real name to Unix UID
- [x] Refactor pyslurm querying using polars instead of nested json
- [ ] Add node-edge graph showing SLURM topology and usage
- [ ] Automate deployment (redeploy when new version is pushed)