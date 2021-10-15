### A Reinforcement Learning Approach to Invoking Positive Behavioural Change
A custom OpenAI gym environment simulating patients behaviour.


### Quick start
Install [Anaconda](https://docs.anaconda.com/anaconda/install/), download our [environment.yml](https://github.com/Capable-project/capable-rl4vc/master/environment.yml) and install using the following command (from Anaconda [documentation](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-from-an-environment-yml-file)):
```sh
> conda env create -f environment.yml
```

The environment name is *rl*. You can activate by executing the following command:
```
(Windows)
> activate rl
(Linux and macOS)
> source activate rl
```
### Alternatively
You can run in docker container. This might first require installation of docker:
```
(Linux)
> curl https://get.docker.com | sh \
  && sudo systemctl --now enable docker
```
Than building an image
```
sudo docker build -t exp .
```
To explore experimental notebooks run 

```
sudo docker run -p 8899:8899 exp:latest jupyter notebook --port=8899 --allow-root --no-browser --ip=0.0.0.0

```