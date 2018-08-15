# Remote Relay Controller

## Install
```bash
npm install
```


## Run
```bash
node app.js 
```

## Use

### Get state of Relay 1
```bash
curl http://localhost:3000/relay/1
```

### Switch OFF relay 3
```bash
curl http://localhost:3000/relay/3/OFF
```

### Switch ON relay 4
```bash
curl http://localhost:3000/relay/4/ON
```

