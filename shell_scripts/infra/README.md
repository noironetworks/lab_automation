This directory contains a script that can be used to sync upstream
repos with downstream forks or mirrors. The shell script must be made
executable:
<pre><code>$ chmod +x sync-repos
</code></pre>

There is one file that the script expects in the local directory:
* sync-list

The file contains the upstream and downstream mapping of repos.

The "repos" subdirectory contains git clones of the upstream repos to sync. The
script will sync every repo found in that directory.

The script can then be run by calling it directly:
<pre><code>$ ./sync-repos
</code></pre>
