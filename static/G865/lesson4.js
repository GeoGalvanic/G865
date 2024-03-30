require(["esri/Map",
  "esri/views/MapView",
  "esri/Basemap",
  "esri/layers/TileLayer",
  "esri/layers/FeatureLayer",
  "esri/portal/PortalItem",
  "esri/portal/Portal",
  "esri/geometry/SpatialReference",
  "esri/geometry/projection",
  "esri/widgets/Editor"
  ], (Map,
    MapView,
    Basemap,
    TileLayer,
    FeatureLayer,
    PortalItem,
    Portal,
    SpatialReference,
    projection,
    Editor
  ) => {
    
    //Connect to cloud pportal
    const portal = new Portal({url: "https://cloud.sarrett.dev/portal"})

    //Create basemap from portal item
    const baseItem = new PortalItem({ id: '418ff66a9f0b4220aa703a2027186e05', portal: portal})
    const baseLayer = new TileLayer({portalItem: baseItem})
    const basemap = new Basemap({
      baseLayers: [ baseLayer]
    })

    //Create the editable feature layer
    const featItem = new PortalItem({
      id: '265952bcff304a5a84f478713893f800',
      portal: portal
    })
    const featLayer = new FeatureLayer ({
      portalItem: featItem,
      spatialReference: {latestWkid: 3857}
    })

    //Create the map and view
    const map = new Map({
        basemap: basemap
      });

    const view = new MapView({
      container: "viewDiv",
      map: map,
      //center: [0,0]
    });

    map.add(featLayer)


    featLayer.when( () => {
      const newRef = new SpatialReference({wkid: 102100})

      featLayer.queryFeatures().then( (fSet) => {
        projection.load().then( () => {
          const featArray  = fSet.features
          featArray.forEach( (feat) => {
            feat.geometry = projection.project(feat.geometry, newRef)
          })
          view.goTo(featArray)
        })
      })
    })

    

    //Add editor widget
    editWidget = new Editor({
      view: view,
    })

    view.ui.add(editWidget)
    
  });