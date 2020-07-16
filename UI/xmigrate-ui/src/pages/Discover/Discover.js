import React, { Component } from 'react'
import { Container, Row, Col, Form, Button } from 'react-bootstrap'
import Tags from "@yaireo/tagify/dist/react.tagify.js";
import "./Discover.scss"
import PostService from '../../services/PostService';
import GetService from '../../services/GetService';
import { DISCOVERURL, STREAMURL } from '../../services/Services';

export default class Discover extends Component {


    constructor(props) {
        super(props)
        this.state = {
            showDiscoverMenu: true,
            showDiscoverMenuEdit: false,
            tags: [],
            email: "",
            password: "",
            provider: "azure",
            project: "testproject",
            message: "",
            disableGoToBlueprint: true
        };
        this.onChange = this.onChange.bind(this)
        this.editDiscover = this.editDiscover.bind(this)
        this.getStream = this.getStream.bind(this)
    }
    onChange(e) {
        // e.persist()
        this.setState({ tags: e.target.value })
    }
    setUsername(e) {
        this.setState({ username: e.target.value })
    }
    setPassword(e) {
        this.setState({ password: e.target.value })
    }
    editDiscover() {
        this.setState({
            showDiscoverMenu: true,
            showDiscoverMenuEdit: false,
        })
    }

    submitDiscover() {
        var hosts = []
        JSON.parse(this.state.tags).map((data) => {
            hosts.push(data.value)
        })
        console.log(hosts);
        var data = {
            "hosts": hosts,
            "username": this.state.username,
            "password": this.state.password,
            "provider": this.state.provider,
            "project": this.state.project
        }
        PostService(DISCOVERURL, data).then((data) => {
            console.log(data)
            var intervalId = setInterval(this.getStream, 3000);
            this.setState({ intervalId: intervalId });
        })
    }

    getStream() {
        GetService(STREAMURL).then((data) => {
            console.log(data);
            if (data.data.offset === "EOF") {
                clearInterval(this.state.intervalId);
            }
            if (data.data.blueprint_status === "success") {
                this.setState({
                    disableGoToBlueprint: false
                })
            }

            this.setState({
                message: data.data.line
            })
        })
    }
    stopStream() {
        clearInterval(this.state.intervalId);
    }
    render() {

        return (
            <div className="Discover media-body background-primary ">
                <Container className="py-5 ">
                    <h4 className="p-0 m-0">
                        Add IP’s of your servers to be migrated
                    </h4>

                    <Row className="py-5 ">
                        <Col md={{ span: 5 }} className="bg-white shadow-sm rounded">
                            <div className="p-3 d-flex flex-column justify-content-between h-100">

                                <div id="discover-menu" className={` ${this.state.showDiscoverMenu ? "" : "d-none"} `}>

                                    <h5>
                                        Server IP's
                                    </h5>

                                    {/* <input type="textarea" name="" id="" /> */}
                                    {/* <Tags mode='textarea' settings={settings} value={value} showDropdown={showDropdown} /> */}
                                    <Tags mode='textarea' onChange={this.onChange} />
                                    <Form className="py-4">
                                        <Form.Group controlId="formBasicEmail" onChange={this.setUsername.bind(this)}>
                                            <Form.Label>Username</Form.Label>
                                            <Form.Control type="text" placeholder="User shouls have sudo access" />
                                        </Form.Group>
                                        <Form.Group controlId="formBasicPassword" onChange={this.setPassword.bind(this)}>
                                            <Form.Label>Password</Form.Label>
                                            <Form.Control type="password" placeholder="Enter the password to be used" />
                                        </Form.Group>
                                        <Button variant="primary" type="button" className="w-100" onClick={this.submitDiscover.bind(this)}>
                                            Submit
                                        </Button>
                                    </Form>
                                </div>

                                <div id="discover-menu-edit" className={` ${this.state.showDiscoverMenuEdit ? "" : "d-none"} `}>
                                    <h5>
                                        Server IP's
                                    </h5>
                                    <div className="pt-4">
                                        <Button variant="success" type="button" disabled className="w-100">
                                            IP-23345-34R35-4545-23R342-2432
                                        </Button>

                                        <p className=" text-center pt-3">
                                            <span className="btn text-primary" onClick={this.editDiscover}> <u> Edit Discovery</u>  </span>
                                        </p>
                                    </div>

                                </div>
                            </div>
                        </Col>
                        <Col md={{ span: 6, offset: 1 }} className="shadow-sm rounded bg-white d-flex flex-column p-0">
                            <div className="p-3 d-flex justify-content-between">
                                <span>
                                    Lorem Ipsum Dollar
                                </span>
                                <Button variant="secondary" disabled={this.state.disableGoToBlueprint} >
                                    Go to Blueprint
                                </Button>
                            </div>

                            <div className="background-primary media-body p-3 discover-logs" >
                                {this.state.message}
                            </div>
                        </Col>
                    </Row>

                </Container>
            </div>
        )
    }
}
