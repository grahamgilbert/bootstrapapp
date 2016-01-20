This is the companion repository to the series on my blog: [Dynamic first boot scripts with Imagr and Flask](http://grahamgilbert.com/blog/2016/01/05/dynamic-first-boot-scripts-with-imagr-and-flask/).

## Example usage

``` bash
$ docker run -d -e BOOTSTRAP_USERNAME=my_username -e BOOTSTRAP_PASSWORD=my_password -v /usr/local/munki_repo:/munki_repo -p 5000:5000 grahamgilbert/bootstrapapp
```
